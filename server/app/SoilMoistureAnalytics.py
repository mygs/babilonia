#!/usr/bin/python3
# -*- coding: utf-8 -*-
import time
import json
import datetime as dt
import logging
import pandas
import requests
from sklearn.linear_model import LinearRegression
from Models import DB, OasisAnalytic
from sqlalchemy import create_engine, func, and_

MOISTURE_PROBES = ['MUX0','MUX1','MUX2','MUX3','MUX4','MUX5','MUX6','MUX7']
ROLLING_WINDOW = 30 # RUPTURE_LEVEL_THRESHOLD and PCT_CHANGE_PERIOD are affected by this value
RUPTURE_LEVEL_THRESHOLD = 0.015
PCT_CHANGE_PERIOD = 10 # RUPTURE_LEVEL_THRESHOLD is affected by this value
HEARTBEAT_PERIOD=30 # (seconds) OMG 2 heartbeats
MOISTURE_DATA_PERIOD = 3600 # (seconds)
PRECIPITATION_PROBABILITY_THRESHOLD=0.25
PRECIPITATION_FORECAST_TIME_AHEAD=3600
LATEST_LEVEL_CHECK_WINDOW=30
LATEST_LEVEL_CHECK_QUANTILE=0.5

class SoilMoistureAnalytics:

    def __init__(self, logger, cfg):
        self.noise_filter_cache = {}
        self.moisture_data_cache = {}
        self.logger = logger
        self.cfg = cfg
        #default values
        self.WINDOW_SIZE = 5
        self.EXPIRE = 3600 # 1 hour
        self.OFFLINE = cfg['MUX_PORT_THRESHOLD']["OFFLINE"]
        self.WET = cfg['MUX_PORT_THRESHOLD']["WET"]
        self.NOSOIL = cfg['MUX_PORT_THRESHOLD']["NOSOIL"]
        self.SCALE = int(self.NOSOIL - self.OFFLINE)
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
        if level <= self.OFFLINE:
            return "rgb(128,128,128)" #grey
        elif level > self.OFFLINE and level < self.NOSOIL:
            dry_level = int(255 * (level-self.OFFLINE)/self.SCALE)
            wet_level = 255 - dry_level
            return "rgb({},0,{})".format(dry_level,wet_level)
        elif level >= self.NOSOIL:
            return "rgb(0,0,0)" # black

    def feedback_online_process(self, feedback):

        timestamp = int(time.time())
        type='feedback'
        node_id = feedback["NODE_ID"]
        status = feedback["IRRIGATION_FEEDBACK"]
        self.logger.debug("[feedback] id:%s => status:%s", node_id, status)

        data = OasisAnalytic(TIMESTAMP=timestamp,
                                NODE_ID=node_id,
                                TYPE=type,
                                DATA=feedback)
        DB.session.merge(data)

    def generate_moisture_req_msg(self, training_feedback_msg):
        return json.dumps({
            'NODE_ID':training_feedback_msg["NODE_ID"],
            'MESSAGE_ID':training_feedback_msg["MESSAGE_ID"],
            'STATUS': ["CAPACITIVEMOISTURE"]
            })

    def default_param(self):
        return {
            'MUX_PORT_THRESHOLD_OFFLINE':self.OFFLINE,
            'MUX_PORT_THRESHOLD_WET':self.WET,
            'MUX_PORT_THRESHOLD_SCALE':self.SCALE,
            'MUX_PORT_THRESHOLD_NOSOIL':self.NOSOIL
            }

    def irrigation_advice(self):
        time_start = dt.datetime.now()

        # 1.0 Refresh cache
        self.refresh_moisture_data_cache()

        for oasis in self.moisture_data_cache:
            # 2.0 Check latest moisture level
            latest_moisture_level = self.get_latest_moisture_level(self.moisture_data_cache[oasis])
            print(latest_moisture_level)
            # 3.0 Apply moving average to reduce noise (req 4.0 and 5.0)
            self.filter_noise_in_moisture_data_cache(oasis)
            # 4.0 Detect rupture
            ruptures = self.detect_rupture_oasis(self.moisture_data_cache[oasis])
            print(ruptures)
            # TODO: 4.1 Rupture alert
            # 5.0 Linear regression
            alpha = self.linear_regressor(self.moisture_data_cache[oasis])
            print(alpha)
            # 6.0 Weather forecast
            will_rain = self.will_rain()
            print("will_rain: "+str(will_rain))
            # TODO: 6.1 Weather alert
            # TODO: 7.0 Irrigation advice
            # Considers data training (or defaults)
            # 8.0 Clear cache
            self.clean_moisture_data_cache()

            time_end = dt.datetime.now()
            elapsed_time = time_end - time_start
            self.logger.info("[irrigation_advice] took %s secs",elapsed_time.total_seconds())

    def get_latest_moisture_level(self, data):
        time_start = dt.datetime.now()
        result = data.tail(LATEST_LEVEL_CHECK_WINDOW).quantile(LATEST_LEVEL_CHECK_QUANTILE).round(0).astype(int)
        time_end = dt.datetime.now()
        elapsed_time = time_end - time_start
        self.logger.info("[get_latest_moisture_level] took %s secs",elapsed_time.total_seconds())
        return result

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
        self.logger.debug("[will_rain] took %s secs",elapsed_time.total_seconds())

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
        #print(self.moisture_data_cache['oasis-39732c'])
