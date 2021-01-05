#!/usr/bin/python3
# -*- coding: utf-8 -*-
import time
import json
import datetime as dt
import logging
import pandas
import requests
from sklearn.linear_model import LinearRegression
from Models import DB, OasisTraining, OasisAnalytic
from sqlalchemy import create_engine, func, and_
from sqlalchemy.orm import sessionmaker

MOISTURE_PROBES = ['MUX0','MUX1','MUX2','MUX3','MUX4','MUX5','MUX6','MUX7']
ROLLING_WINDOW = 30 # RUPTURE_LEVEL_THRESHOLD and PCT_CHANGE_PERIOD are affected by this value
RUPTURE_LEVEL_THRESHOLD = 0.015
PCT_CHANGE_PERIOD = 10 # RUPTURE_LEVEL_THRESHOLD is affected by this value
HEARTBEAT_PERIOD=30 # (seconds) OMG 2 heartbeats
MOISTURE_DATA_PERIOD = 3*3600 # (seconds)
FORECAST_TIME_AHEAD = MOISTURE_DATA_PERIOD
PRECIPITATION_PROBABILITY_THRESHOLD=0.25
PRECIPITATION_FORECAST_TIME_AHEAD=3600
LATEST_LEVEL_CHECK_WINDOW=30
LATEST_LEVEL_CHECK_QUANTILE=0.5
LN_SCORE_THRESHOLD=0.3

class SoilMoistureAnalytics:

    def __init__(self, logger, cfg):
        self.noise_filter_cache = {}
        self.moisture_data_cache = {}
        self.logger = logger
        self.cfg = cfg
        #default values
        self.WINDOW_SIZE = 5
        self.EXPIRE = 3600 # 1 hour
        self.DEFAULT_OFFLINE = int(cfg['MUX_PORT_THRESHOLD']["OFFLINE"])
        self.DEFAULT_WET = int(cfg['MUX_PORT_THRESHOLD']["WET"])
        self.DEFAULT_NOSOIL = int(cfg['MUX_PORT_THRESHOLD']["NOSOIL"])
        self.SCALE = int(self.DEFAULT_NOSOIL - self.DEFAULT_OFFLINE)
        self.SQLALCHEMY_DATABASE_URI =  cfg["SQLALCHEMY_DATABASE_URI"]


    def gui_noise_filter(self, node_id, timestamp, moisture):
        cache_entry = self.noise_filter_cache.get(node_id)
        if cache_entry == None or (timestamp - cache_entry['TIMESTAMP']) > self.EXPIRE:
            self.logger.debug("[SoilMoistureAnalytics] new or expired cache")
            cache_entry = { 'SAMPLE':0,
                            'TIMESTAMP':timestamp,
                            'AVERAGE':moisture}

        AVERAGE = cache_entry['AVERAGE']
        SAMPLE = cache_entry['SAMPLE'] + 1
        N = min(SAMPLE, self.WINDOW_SIZE)

        for i in range(8):
            idx = 'MUX'+str(i)
            avg_mux = AVERAGE.get(idx,0)
            AVERAGE[idx] = int((avg_mux*(N-1) + moisture[idx])/N)

        self.noise_filter_cache[node_id] = { 'SAMPLE':SAMPLE,
                                          'TIMESTAMP':timestamp,
                                            'AVERAGE':AVERAGE}
        return AVERAGE

    def status(self, node_id, port, level):
        #analytics = DB.session.query(OasisAnalytic).first()
        #self.logger.debug("[SoilMoistureAnalytics] %s", analytics.data())
        #TODO: put some brain in here
        if level <= self.DEFAULT_OFFLINE:
            return "rgb(128,128,128)" #grey
        elif level > self.DEFAULT_OFFLINE and level < self.DEFAULT_NOSOIL:
            dry_level = int(255 * (level-self.DEFAULT_OFFLINE)/self.SCALE)
            wet_level = 255 - dry_level
            return "rgb({},0,{})".format(dry_level,wet_level)
        elif level >= self.DEFAULT_NOSOIL:
            return "rgb(0,0,0)" # black

    def feedback_online_process(self, feedback):

        timestamp = int(time.time())
        node_id = feedback["NODE_ID"]
        message_id = feedback["MESSAGE_ID"]
        value = feedback["IRRIGATION_FEEDBACK"]
        self.logger.debug("[feedback] id:%s => value:%s", node_id, value)

        data = OasisTraining(NODE_ID=node_id,
                             VALUE=value,
                             MESSAGE_ID=message_id,
                             TIMESTAMP=timestamp)
        DB.session.merge(data)

    def generate_moisture_req_msg(self, training_feedback_msg):
        return json.dumps({
            'NODE_ID':training_feedback_msg["NODE_ID"],
            'MESSAGE_ID':training_feedback_msg["MESSAGE_ID"],
            'STATUS': ["CAPACITIVEMOISTURE"]
            })

    def default_param(self):
        return {
            'MUX_PORT_THRESHOLD_OFFLINE':self.DEFAULT_OFFLINE,
            'MUX_PORT_THRESHOLD_WET':self.DEFAULT_WET,
            'MUX_PORT_THRESHOLD_SCALE':self.SCALE,
            'MUX_PORT_THRESHOLD_NOSOIL':self.DEFAULT_NOSOIL
            }

    def irrigation_advice(self):
        time_start = dt.datetime.now()
        advice = {}
        nodes = {}
        # Refresh cache
        self.refresh_moisture_data_cache()
        # Considers data training
        training_data = self.get_training_data()
        # Weather forecast
        will_rain = self.will_rain()

        advice['will_rain'] = will_rain
        for oasis in self.moisture_data_cache:
            # Calculate moisture threshold based on training data
            moisture_threshold_level = self.moisture_threshold_level(training_data)
            # Check latest moisture level
            latest_moisture_level = self.get_latest_moisture_level(self.moisture_data_cache[oasis])
            # Verifying valid probes
            valid_probes = latest_moisture_level[
                                    (latest_moisture_level > self.DEFAULT_OFFLINE) &
                                    (latest_moisture_level < self.DEFAULT_NOSOIL)
                                ].index.values
            # Filter valid probes
            latest_moisture_level = latest_moisture_level.loc[latest_moisture_level.index.intersection(valid_probes)]
            # Apply moving average to reduce noise
            self.filter_noise_in_moisture_data_cache(oasis)
            # Detect rupture
            #ruptures = self.detect_rupture_oasis(self.moisture_data_cache[oasis])
            # TODO: Rupture alert
            # Linear regression
            alpha = self.linear_regressor(self.moisture_data_cache[oasis])
            # Irrigation advice
            forecast = self.forecast_moisture_level(will_rain,
                                                    alpha,
                                                    latest_moisture_level,
                                                    moisture_threshold_level)
            nodes[oasis] = forecast

        advice['nodes'] = nodes
        # Clear cache
        self.clean_moisture_data_cache()
        # Saving the Advice
        engine = create_engine(self.SQLALCHEMY_DATABASE_URI)
        session = sessionmaker(bind=engine)()
        data = OasisAnalytic(TIMESTAMP=int(time.time()),
                             TYPE='nodes',
                             DATA=advice
                             )
        session.merge(data)
        session.commit()
        time_end = dt.datetime.now()
        elapsed_time = time_end - time_start
        self.logger.info("[irrigation_advice] took %s secs",elapsed_time.total_seconds())
        return json.dumps(advice)

    def forecast_moisture_level(self, will_rain, alpha, latest_moisture_level, moisture_threshold_level):
        forecast = {}
        need_water_probes = 0
        entries={}

        total_probes = len(latest_moisture_level)
        for index, value in latest_moisture_level.items():
            entry={}
            threshold = moisture_threshold_level.get(index)
            coef = alpha.coef.get(index)
            score = alpha.score.get(index)
            future_value = value
            if score >= LN_SCORE_THRESHOLD:
                future_value += (coef*FORECAST_TIME_AHEAD).round(0).astype(int)
            if future_value >= threshold:
                need_water_probes+=1

            entry['actual_value'] = str(value)
            entry['threshold'] = str(threshold)
            entry['coef'] = str(float("{:.3f}".format(coef)))
            entry['score'] = str(float("{:.3f}".format(score)))
            entry['future_value'] = str(future_value)
            entries[index] = entry

        result =  float("{:.3f}".format(need_water_probes/total_probes))
        forecast['result'] = str(result)
        if result >= 0.5:
            if will_rain:
                forecast['advice'] = 'POSPONE'
            else:
                forecast['advice'] = 'IRRIGATE'
        else:
            forecast['advice'] = 'IGNORE'
        forecast['details'] = entries
        return forecast


    def get_latest_moisture_level(self, data):
        time_start = dt.datetime.now()
        result = data.tail(LATEST_LEVEL_CHECK_WINDOW).quantile(LATEST_LEVEL_CHECK_QUANTILE).round(0).astype(int)
        time_end = dt.datetime.now()
        elapsed_time = time_end - time_start
        self.logger.info("[get_latest_moisture_level] took %s secs",elapsed_time.total_seconds())
        self.logger.debug(result)
        return result

    def moisture_threshold_level_valid_value(self, value):
        if len(value) == 0:
            return False
        else:
            iv = int(value)
            if (iv < self.DEFAULT_OFFLINE) | (iv > self.DEFAULT_NOSOIL):
                return False
        return True

    def moisture_threshold_level(self, node_training):
        probes_moisture_level={}
        dry = node_training.loc[node_training['VALUE'] == 'soil_dry']
        wet = node_training.loc[node_training['VALUE'] == 'soil_wet']
        default = self.DEFAULT_WET

        for probe in MOISTURE_PROBES:
            if not self.moisture_threshold_level_valid_value(dry[probe]):
                if not self.moisture_threshold_level_valid_value(wet[probe]):
                    # SCENARIO A: No training feedback. Use defaults
                    probes_moisture_level[probe] = default
                else:
                    wp = int(wet[probe])
                    #  There is ONLY wet threshold feedback
                    if wp > default:
                        # SCENARIO F: Change wet threshold due the feedback
                        probes_moisture_level[probe] = wp
                    else:
                        # SCENARIO E: Do not change wet threshold. Default level might be ok
                        probes_moisture_level[probe] = default
            else:
                if not self.moisture_threshold_level_valid_value(wet[probe]):
                    #  There is ONLY dry threshold feedback
                    dp = int(dry[probe])
                    if dp < default:
                        # SCENARIO G: Change wet threshold due the feedback
                        probes_moisture_level[probe] = dp
                    else:
                        # SCENARIO D: Do not change wet threshold. Default level might be ok
                        probes_moisture_level[probe] = default
                else:
                    # There are dry and wet feedbacks
                    wp = int(wet[probe])
                    dp = int(dry[probe])
                    if wp < default:
                        if dp > default:
                            # SCENARIO A: Lets keep current default threshold
                            probes_moisture_level[probe] = default
                        else:
                            if wp > dp:
                                # Strange scenario
                                probes_moisture_level[probe] = default
                            else:
                            # SCENARIO C: Dry and Wet feedbacks are LOWER than current threshold
                                probes_moisture_level[probe] = (dp + wp)/2
                    else:
                        # SCENARIO B: Dry and Wet feedbacks are HIGHER than current threshold
                        probes_moisture_level[probe] = (dp + wp)/2

        return pandas.Series(probes_moisture_level)


    def linear_regressor(self, data):
        time_start = dt.datetime.now()
        X = data.index.to_numpy().reshape(-1, 1)
        entries={}
        for mux in MOISTURE_PROBES:
            Y = data[mux].values.reshape(-1, 1)
            linear_regressor = LinearRegression()  # create object for the class
            linear_regressor.fit(X, Y)  # perform linear regression
            Y_pred = linear_regressor.predict(X)  # make predictions
            entry={}
            entry['score']=linear_regressor.score(X,Y)
            entry['coef'] =linear_regressor.coef_[0][0]
            entries[mux] = entry
        result = pandas.DataFrame(data=entries).T # transpose
        time_end = dt.datetime.now()
        elapsed_time = time_end - time_start
        self.logger.info("[linear_regressor] took %s secs",elapsed_time.total_seconds())
        self.logger.debug(result)
        return result

    def detect_rupture_oasis(self, data):
        time_start = dt.datetime.now()
        #Percentage change between the current and a prior element
        # Finding negative or positive slopes ...
        pct_change_series = data.pct_change(periods=PCT_CHANGE_PERIOD).dropna()
        ruptures={}
        min_probes={}
        max_probes={}
        for mux in MOISTURE_PROBES:
            min_entry={}
            min_entry['epoch'] = pct_change_series[mux].idxmin()
            min_entry['value'] = pct_change_series[mux][min_entry['epoch']]
            if min_entry['value'] < -RUPTURE_LEVEL_THRESHOLD:
                min_probes[mux] = min_entry

            max_entry={}
            max_entry['epoch'] = pct_change_series[mux].idxmax()
            max_entry['value'] = pct_change_series[mux][max_entry['epoch']]
            if max_entry['value'] > RUPTURE_LEVEL_THRESHOLD:
                max_probes[mux] = max_entry
        ruptures['downward'] = pandas.DataFrame(data=min_probes).T
        ruptures['upward'] =  pandas.DataFrame(data=max_probes).T

        time_end = dt.datetime.now()
        elapsed_time = time_end - time_start
        self.logger.info("[detect_rupture_oasis] took %s secs",elapsed_time.total_seconds())
        self.logger.debug(ruptures)
        return ruptures

    def will_rain(self):
        time_start = dt.datetime.now()
        will_rain = False
        weather_key = self.cfg["WEATHER_KEY"]
        lat = self.cfg["LATITUDE"]
        long = self.cfg["LONGITUDE"]
        try:
            response = requests.get(
            'https://api.forecast.io/forecast/%s/%s,%s?units=si&lang=pt&exclude=currently,flags,alerts,daily'
            %(weather_key, lat, long))
            data = response.json()
            hourly_forecast = pandas.DataFrame(data=data["hourly"]["data"])
            hourly_forecast.set_index('time', inplace=True)
            now = int(time_start.timestamp())
            hourly_forecast_filtered = hourly_forecast[ (hourly_forecast.index >= now ) &
                                                        (hourly_forecast.index <= now + PRECIPITATION_FORECAST_TIME_AHEAD)]
            will_rain = len(hourly_forecast_filtered[
                    (hourly_forecast_filtered['precipProbability'] >= PRECIPITATION_PROBABILITY_THRESHOLD) |
                    (hourly_forecast_filtered['icon'] == 'rain')]) > 0
        except requests.ConnectionError:
            self.logger.debug("[will_rain] ConnectionError!!!")

        time_end = dt.datetime.now()
        elapsed_time = time_end - time_start
        self.logger.info("[will_rain] took %s secs",elapsed_time.total_seconds())
        self.logger.debug("will_rain: "+str(will_rain))
        return will_rain


    def clean_moisture_data_cache(self):
        self.moisture_data_cache = {}

    def filter_noise_in_moisture_data_cache(self, oasis):
        time_start = dt.datetime.now()
        self.moisture_data_cache[oasis] = self.moisture_data_cache[oasis].rolling(ROLLING_WINDOW).mean().dropna()
        time_end = dt.datetime.now()
        elapsed_time = time_end - time_start
        self.logger.info("[filter_noise_in_moisture_data_cache] %s took %s secs",oasis, elapsed_time.total_seconds())

    def refresh_moisture_data_cache(self):
        time_start = dt.datetime.now()

        self.clean_moisture_data_cache()
        engine = create_engine(self.SQLALCHEMY_DATABASE_URI)
        ############# get alive nodes #############
        now = int(time.time())
        period_for_last_heartbeat = int(now - HEARTBEAT_PERIOD)
        period_for_last_moisture_data = int(now - MOISTURE_DATA_PERIOD)

        nodes = pandas.read_sql_query(
            """
            SELECT NODE_ID
            FROM OASIS_HEARTBEAT
            WHERE LAST_UPDATE >= {}
            """.format(period_for_last_heartbeat),
            engine)
        for index,node in nodes.iterrows():
            #### get moisture data from alive nodes ####
            node_id = node['NODE_ID']

            self.moisture_data_cache[node_id] = pandas.read_sql_query(
                """
                SELECT  TIMESTAMP,
                        DATA->'$.DATA.CAPACITIVEMOISTURE.MUX0' AS MUX0,
                        DATA->'$.DATA.CAPACITIVEMOISTURE.MUX1' AS MUX1,
                        DATA->'$.DATA.CAPACITIVEMOISTURE.MUX2' AS MUX2,
                        DATA->'$.DATA.CAPACITIVEMOISTURE.MUX3' AS MUX3,
                        DATA->'$.DATA.CAPACITIVEMOISTURE.MUX4' AS MUX4,
                        DATA->'$.DATA.CAPACITIVEMOISTURE.MUX5' AS MUX5,
                        DATA->'$.DATA.CAPACITIVEMOISTURE.MUX6' AS MUX6,
                        DATA->'$.DATA.CAPACITIVEMOISTURE.MUX7' AS MUX7
                FROM OASIS_DATA
                WHERE NODE_ID = '{}'
                      AND  json_length(DATA->'$.DATA.CAPACITIVEMOISTURE') > 0
                      AND TIMESTAMP >= {}
                ORDER BY TIMESTAMP asc
                """.format(node_id, period_for_last_moisture_data),
                engine).astype(int)
            self.moisture_data_cache[node_id].set_index('TIMESTAMP', inplace=True)
        time_end = dt.datetime.now()
        elapsed_time = time_end - time_start
        self.logger.info("[refresh_moisture_data_cache] took %s secs",elapsed_time.total_seconds())
        self.logger.debug(self.moisture_data_cache[node['NODE_ID']])


    def get_training_data(self):
        time_start = dt.datetime.now()
        engine = create_engine(self.SQLALCHEMY_DATABASE_URI)
        training_data = pandas.read_sql_query(
            """
                SELECT
                	OA.NODE_ID,
                    OA.VALUE,
                	OD.DATA->'$.DATA.CAPACITIVEMOISTURE.MUX0' AS MUX0,
                	OD.DATA->'$.DATA.CAPACITIVEMOISTURE.MUX1' AS MUX1,
                	OD.DATA->'$.DATA.CAPACITIVEMOISTURE.MUX2' AS MUX2,
                	OD.DATA->'$.DATA.CAPACITIVEMOISTURE.MUX3' AS MUX3,
                	OD.DATA->'$.DATA.CAPACITIVEMOISTURE.MUX4' AS MUX4,
                	OD.DATA->'$.DATA.CAPACITIVEMOISTURE.MUX5' AS MUX5,
                	OD.DATA->'$.DATA.CAPACITIVEMOISTURE.MUX6' AS MUX6,
                	OD.DATA->'$.DATA.CAPACITIVEMOISTURE.MUX7' AS MUX7
                FROM farmland.OASIS_TRAINING OA
                    INNER JOIN farmland.OASIS_DATA OD
                ON
                	OA.NODE_ID = OD.NODE_ID
                WHERE
                	OA.MESSAGE_ID = OD.DATA->'$.MESSAGE_ID'
            """,engine)
        #training_data.set_index('NODE_ID', inplace=True) # multiple node_id entries
        for col in MOISTURE_PROBES:
            training_data[col] = training_data[col].astype(int)
        time_end = dt.datetime.now()
        elapsed_time = time_end - time_start
        self.logger.info("[get_training_data] took %s secs",elapsed_time.total_seconds())
        self.logger.debug(training_data)
        return training_data
