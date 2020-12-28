#!/usr/bin/python3
# -*- coding: utf-8 -*-
import time
import json
import datetime as dt
import logging
import pandas
from Models import DB, OasisAnalytic
from sqlalchemy import create_engine, func, and_

MOISTURE_PROBES = ['MUX0','MUX1','MUX2','MUX3','MUX4','MUX5','MUX7']
ROLLING_WINDOW = 30 # RUPTURE_LEVEL_THRESHOLD and PCT_CHANGE_PERIOD are affected by this value
RUPTURE_LEVEL_THRESHOLD = 0.015
PCT_CHANGE_PERIOD = 10 # RUPTURE_LEVEL_THRESHOLD is affected by this value
HEARTBEAT_PERIOD=30 # (seconds) OMG 2 heartbeats
MOISTURE_DATA_PERIOD = 3600 # (seconds)

class SoilMoistureAnalytics:

    def __init__(self, logger, cfg):
        self.noise_filter_cache = {}
        self.moisture_data_cache = {}
        self.logger = logger
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
        # 1.0 Refresh cache
        self.refresh_moisture_data_cache()

        for oasis in self.moisture_data_cache:
            # 2.0 Detect rupture
            ruptures = self.detect_rupture_oasis(self.moisture_data_cache[oasis])
            print(ruptures)
            # TODO: 2.1 Rupture alert
            # TODO: 3.0 Linear regression
            # TODO: 4.0 Weather forecast
            # TODO: 5.0 Check latest moisture level
            # TODO: 6.0 Irrigation advice
            # TODO: 7.0 Clear cache


    def detect_rupture_oasis(self, data):
        time_start = dt.datetime.now()
        # Filtering the noise ...
        data_filtered = data.rolling(ROLLING_WINDOW).mean().dropna()
        #Percentage change between the current and a prior element
        # Finding negative or positive slopes ...
        pct_change_series = data_filtered.pct_change(periods=PCT_CHANGE_PERIOD).dropna()
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
        ruptures['negative'] = pandas.DataFrame(data=min_probes).T
        ruptures['positive'] =  pandas.DataFrame(data=max_probes).T

        time_end = dt.datetime.now()
        elapsed_time = time_end - time_start
        self.logger.info("[detect_rupture_oasis] took %s secs",elapsed_time.total_seconds())

        return ruptures

    def clean_moisture_data_cache(self):
        self.moisture_data_cache = {}

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
                engine)
            self.moisture_data_cache[node_id].set_index('TIMESTAMP', inplace=True)
        time_end = dt.datetime.now()
        elapsed_time = time_end - time_start
        self.logger.info("[refresh_moisture_data_cache] took %s secs",elapsed_time.total_seconds())
        #print(self.moisture_data_cache['oasis-39732c'])
