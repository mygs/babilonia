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

HEARTBEAT_PERIOD=5*60 # (seconds) OMG 5 min

class Irrigation:

    def __init__(self, logger, cfg, mqtt, socketio, oasis_properties):
        self.logger = logger
        self.cfg = cfg
        self.mqtt = mqtt
        self.socketio = socketio
        self.oasis_properties = oasis_properties
        self.SQLALCHEMY_DATABASE_URI =  cfg["SQLALCHEMY_DATABASE_URI"]
        self.IRRIGATION_DURATION =  cfg["IRRIGATION"]["DURATION"] # seconds
        self.nodes_postponed_to_next_irrigation = []

    def run_dummy(self):
        ############# get latest moisture analytics result #############
        engine = create_engine(self.SQLALCHEMY_DATABASE_URI)
        analytics = pandas.read_sql_query(
            """
            SELECT TIMESTAMP, DATA
            FROM OASIS_ANALYTIC
            WHERE TYPE='advice'
            ORDER BY TIMESTAMP DESC LIMIT 1
            """, engine)
        if not analytics.empty:
            self.logger.info("[irrigation] ***** STARTING DUMMY IRRIGATION *****")
            moisture_analytics_last_calculation = dt.datetime.fromtimestamp(int(analytics['TIMESTAMP'].iloc[0])).strftime('%Y-%m-%d %H:%M:%S')
            data = json.loads(analytics['DATA'].iloc[0])
            self.logger.info("[irrigation] Found moisture analytics calculated in: %s",moisture_analytics_last_calculation)
            if  data['will_rain']:
                self.logger.info("[irrigation] Weather forecast says it WILL rain")
            else:
                self.logger.info("[irrigation] Weather forecast says it WONT rain")

            nodes_lst = []
            for node in data['node']:
                advice = data['node'][node]['advice']
                self.logger.info("[irrigation] %s => %s", self.oasis_properties[node]["name"], advice)
                if advice == "IRRIGATE":
                    nodes_lst.append(node)

            self.logger.info("[irrigation] ***** ENDING DUMMY IRRIGATION *****")
        else:
            self.logger.info("[irrigation] Skipping DUMMY IRRIGATION due Moisture analytics not found")

    def run_smart(self):
        ############# get latest moisture analytics result #############
        engine = create_engine(self.SQLALCHEMY_DATABASE_URI)
        analytics = pandas.read_sql_query(
            """
            SELECT TIMESTAMP, DATA
            FROM OASIS_ANALYTIC
            WHERE TYPE='advice'
            ORDER BY TIMESTAMP DESC LIMIT 1
            """, engine)
        if not analytics.empty:
            self.logger.info("[irrigation] ***** STARTING SMART IRRIGATION *****")
            moisture_analytics_last_calculation = dt.datetime.fromtimestamp(int(analytics['TIMESTAMP'].iloc[0])).strftime('%Y-%m-%d %H:%M:%S')
            data = json.loads(analytics['DATA'].iloc[0])
            self.logger.info("[irrigation] Found moisture analytics calculated in: %s",moisture_analytics_last_calculation)
            if  data['will_rain']:
                self.logger.info("[irrigation] Weather forecast says it WILL rain")
            else:
                self.logger.info("[irrigation] Weather forecast says it WONT rain")

            nodes_to_irrigate = []
            nodes_postponed_last_irrigation = []
            nodes_postponed_last_irrigation.extend(self.nodes_postponed_to_next_irrigation)
            self.nodes_postponed_to_next_irrigation = []

            for node in data['node']:
                advice = data['node'][node]['advice']
                self.logger.info("[irrigation] advice %s => %s", self.oasis_properties[node]["name"], advice)
                if advice == "IRRIGATE":
                    if node not in nodes_to_irrigate:
                        nodes_to_irrigate.append(node)
                if advice == "POSTPONE":
                    if node not in nodes_postponed_last_irrigation:
                        self.nodes_postponed_to_next_irrigation.append(node)
                    else:
                        self.logger.info("[irrigation] postponed before, but it will be irrigate this time => %s", self.oasis_properties[node]["name"])
                        nodes_to_irrigate.append(node)

            nodes_df = pandas.DataFrame(nodes_to_irrigate, columns =['NODE_ID'])
            self.run(nodes_df)

            self.logger.info("[irrigation] ***** ENDING SMART IRRIGATION *****")
        else:
            self.logger.info("[irrigation] Skipping SMART IRRIGATION due Moisture analytics not found")

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

        monitor_msg = {
                      'irrigation':{
                            'mode': 'standard',
                            'duration': self.IRRIGATION_DURATION,
                            'nodes':nodes['NODE_ID'].values.tolist(),
                            'status': 'started'
                            }
                        }
        self.socketio.emit('ws-server-monitor', data=monitor_msg)
        self.run(nodes)
        monitor_msg['irrigation']['status'] = 'finished'

        self.socketio.emit('ws-server-monitor', data=monitor_msg)

        self.logger.info("[irrigation] ***** ENDING STANDARD IRRIGATION *****")


    def run(self, nodes):
        nodes_to_irrigate = len(nodes.index)
        self.logger.info("[irrigation] %d nodes will receive water.",nodes_to_irrigate)

        if nodes_to_irrigate > 0:
            url = 'http://%s/water-tank'%(self.cfg["WATER_TANK_SERVER"])
            headers = {'Content-type': 'application/json'}
            response = requests.post(url,data=json.dumps({'DIRECTION':'OUT', 'ACTION':True }), headers=headers)
            self.logger.info("[irrigation]  Water tank server response: %s", response)

            if response.status_code != 200:
                self.logger.info("[irrigation] Water Tank connection http status code: %s!!!", str(response.status_code))

            node_id = None
            for index,node in nodes.iterrows():
                node_id = node['NODE_ID']
                message = json.dumps({'NODE_ID': str(node_id), 'MESSAGE_ID':"water_sched", 'COMMAND':{"WATER": True}})
                self.logger.info("[irrigation] %s", message)
                self.mqtt.publish("/oasis-inbound", message)
                time.sleep(self.IRRIGATION_DURATION)
                #message = json.dumps({'NODE_ID': str(node_id), 'MESSAGE_ID':"water_sched", 'COMMAND':{"WATER": False}})
                message = json.dumps({'NODE_ID': 'ALL', 'MESSAGE_ID':"water_sched", 'COMMAND':{"WATER": False}})
                self.mqtt.publish("/oasis-inbound", message)
                self.logger.info("[irrigation] %s", message)


            message = json.dumps({'NODE_ID': 'ALL', 'MESSAGE_ID':"water_sched", 'COMMAND':{"WATER": False}})
            self.logger.info("[irrigation] %s", message)
            self.mqtt.publish("/oasis-inbound", message)

            requests.post(url,data=json.dumps({'DIRECTION':'OUT', 'ACTION':False }), headers=headers)
        else:
            self.logger.info("[irrigation] skip irrigation procedures")


if __name__ == '__main__':
    print("*** STARTING Irrigation Test ***")
    app = Irrigation()
    app.monitorTankLevel()
    while True:
        time.sleep(3)
        print("*")
