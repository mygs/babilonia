#!/usr/bin/python3
# -*- coding: utf-8 -*-
import time
import json
import datetime as dt
import logging
import pandas
import requests
from Models import DB, OasisTraining, OasisAnalytic
from sqlalchemy import create_engine, func, and_
from sqlalchemy.orm import sessionmaker

IRRIGATION_DURATION = 5*60 #seconds
HEARTBEAT_PERIOD=5*60 # (seconds) OMG 5 min

class Irrigation:

    def __init__(self, logger, cfg, mqtt):
        self.logger = logger
        self.cfg = cfg
        self.mqtt = mqtt
        self.SQLALCHEMY_DATABASE_URI =  cfg["SQLALCHEMY_DATABASE_URI"]

    def run_standard(self):
        self.logger.info("[irrigation] ***** STARTING STANDARD IRRIGATION *****")
        ############# get all alive nodes #############
        now = int(time.time())
        period_for_last_heartbeat = int(now - HEARTBEAT_PERIOD)
        engine = create_engine(self.SQLALCHEMY_DATABASE_URI)
        nodes = pandas.read_sql_query(
            """
            SELECT NODE_ID
            FROM OASIS_HEARTBEAT
            WHERE LAST_UPDATE >= {}
            """.format(period_for_last_heartbeat),
            engine)

        self.run(nodes)
        self.logger.info("[irrigation] ***** ENDING STANDARD IRRIGATION *****")



    def run(self, nodes):

        url = 'http://%s/water-tank'%(self.cfg["WATER_TANK_SERVER"])
        headers = {'Content-type': 'application/json'}
        response = requests.post(url,data=json.dumps({'DIRECTION':'OUT', 'ACTION':True }), headers=headers)
        self.logger.info("[irrigation]  Water tank server response: %s", response)

        if response.status_code != 200:
            self.logger.info("[irrigation] Water Tank connection http status code: %s!!!", str(response.status_code))

        node_id = None
        self.logger.info("[irrigation] %d nodes will receive water.",len(nodes.index))
        for index,node in nodes.iterrows():
            node_id = node['NODE_ID']
            message = json.dumps({'NODE_ID': str(node_id), 'MESSAGE_ID':"water_sched", 'COMMAND':{"WATER": True}})
            self.logger.info("[irrigation] %s", message)
            self.mqtt.publish("/oasis-inbound", message)
            time.sleep(IRRIGATION_DURATION)
            message = json.dumps({'NODE_ID': str(node_id), 'MESSAGE_ID':"water_sched", 'COMMAND':{"WATER": False}})
            self.mqtt.publish("/oasis-inbound", message)
            self.logger.info("[irrigation] %s", message)

        requests.post(url,data=json.dumps({'DIRECTION':'OUT', 'ACTION':False }), headers=headers)


if __name__ == '__main__':
    print("*** STARTING Irrigation Test ***")
    app = Irrigation()
    app.monitorTankLevel()
    while True:
        time.sleep(3)
        print("*")
