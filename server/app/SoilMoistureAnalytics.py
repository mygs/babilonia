#!/usr/bin/python3
# -*- coding: utf-8 -*-
import json
import time
from Models import *
from sqlalchemy import func, and_
import logging

class SoilMoistureAnalytics:

    def __init__(self, logger, defaults):
        self.cache = {}
        self.logger = logger
        #default values
        self.WINDOW_SIZE = 5
        self.OFFLINE = defaults["OFFLINE"]
        self.WET = defaults["WET"]
        self.NOSOIL = defaults["NOSOIL"]

    def gui_noise_filter(self, node_id, timestamp, moisture):
        cache_entry = self.cache.get(node_id, { 'SAMPLE':0,
                                                'TIMESTAMP':timestamp,
                                                'AVERAGE':moisture})
        AVERAGE = cache_entry['AVERAGE']
        SAMPLE = cache_entry['SAMPLE'] + 1
        N = min(SAMPLE, self.WINDOW_SIZE)

        for i in range(8):
            idx = 'MUX'+str(i)
            avg_mux = AVERAGE.get(idx,0)
            AVERAGE[idx] = int((avg_mux*(N-1) + moisture[idx])/N)

        self.cache[node_id] = { 'SAMPLE':SAMPLE,
                                'TIMESTAMP':timestamp,
                                'AVERAGE':AVERAGE}
        return AVERAGE

    def status(self, node_id, port, level):
        #analytics = DB.session.query(OasisAnalytic).first()
        #self.logger.debug("[SoilMoistureAnalytics] %s", analytics.data())
        #TODO: put some brain in here
        if level <= self.OFFLINE:
            return "moisture-offline"
        elif level > self.OFFLINE and level <= self.WET:
            return "moisture-wet"
        elif level > self.WET and level < self.NOSOIL:
            return "moisture-dry"
        elif level >= self.NOSOIL:
            return "moisture-nosoil"

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
        DB.session.add(data)
        '''

        latest = DB.session.query(func.max(OasisData.TIMESTAMP).label('TIMESTAMP')).filter(
                    OasisData.DATA['DATA']['NODE'].isnot(None)).filter(
                        OasisData.NODE_ID==node_id).group_by(OasisData.NODE_ID).subquery('t2')
        latest_node_data = DB.session.query(OasisData).join(
            latest, and_(OasisData.TIMESTAMP == latest.c.TIMESTAMP))
        self.logger.debug("[feedback-data] %s", latest_node_data)

        if status == "wet":
            self.logger.debug("[STATUS]>>>>>>>>WET<<<<<<<<<")
        if status == "dry":
            self.logger.debug("[STATUS]>>>>>>>>DRY<<<<<<<<<")
        '''

    def param(self):
        return json.dumps(
            {'MUX_PORT_THRESHOLD_OFFLINE':self.OFFLINE,
            'MUX_PORT_THRESHOLD_WET':self.WET,
            'MUX_PORT_THRESHOLD_NOSOIL':self.NOSOIL})
