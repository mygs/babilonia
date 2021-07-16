#!/usr/bin/python3
# -*- coding: utf-8 -*-
import time
import json
import datetime as dt
import logging
import pandas
import requests
from Models import DB, OasisTraining, OasisAnalytic
from TelegramAssistantServer import *
from sqlalchemy import create_engine, func, and_
from sqlalchemy.orm import sessionmaker

HEARTBEAT_PERIOD = 5 * 60  # (seconds) OMG 5 min
MOISTURE_PROBES = ['MUX0','MUX1','MUX2','MUX3','MUX4','MUX5','MUX6','MUX7']


class Irrigation:
    def __init__(self, logger, cfg, mqtt, socketio, oasis_properties):
        self.logger = logger
        self.cfg = cfg
        self.mqtt = mqtt
        self.socketio = socketio
        self.oasis_properties = oasis_properties
        self.SQLALCHEMY_DATABASE_URI = cfg["SQLALCHEMY_DATABASE_URI"]
        self.IRRIGATION_DURATION = cfg["IRRIGATION"]["DURATION"]  # seconds
        self.nodes_postponed_to_next_irrigation = []

    def run_inspector(self):
        ############# get latest moisture analytics result #############
        engine = create_engine(self.SQLALCHEMY_DATABASE_URI)
        analytics = pandas.read_sql_query(
            """
            SELECT TIMESTAMP, DATA
            FROM OASIS_ANALYTIC
            WHERE TYPE='advice'
            ORDER BY TIMESTAMP DESC LIMIT 1
            """,
            engine,
        )
        if not analytics.empty:
            analytic_data = json.loads(analytics["DATA"].iloc[0])
            analytic_timestamp = int(analytics["TIMESTAMP"].iloc[0])
            self.logger.info("[inspector] ***** STARTING IRRIGATION INSPECTOR *****")
            monitor_message = "<b>IRRIGATION INSPECTOR</b>\n<pre>\n"
            monitor_message += "{0:10} {1}\n".format("", " 0 1 2 3 4 5 6 7")
            for node in analytic_data["node"]:
                advice = analytic_data["node"][node]["advice"]
                if advice == "IRRIGATE":
                    node_water_median_timestamp = pandas.read_sql_query(
                        """
                        SELECT IFNULL(ROUND(AVG(TIMESTAMP),0),0) AS TIMESTAMP
                        FROM OASIS_DATA 
                        WHERE 	NODE_ID = '{}'   
                                AND  json_length(DATA->'$.DATA') > 0 
                                AND DATA->'$.DATA.WATER' = 1
                                AND TIMESTAMP > {}
                        """.format(node, analytic_timestamp), engine)
                    
                    last_irrigation_timestamp = int(node_water_median_timestamp['TIMESTAMP'].iloc[0])

                    if last_irrigation_timestamp == 0:
                        result += "❌❌❌❌❌❌❌❌"
                    else:
                        inspection_delta_time = self.cfg["IRRIGATION"]["INSPECTION_SAMPLE_DELTA_TIME"]
                        end_timestamp_before_irrigation = last_irrigation_timestamp - self.IRRIGATION_DURATION
                        start_timestamp_before_irrigation = end_timestamp_before_irrigation - inspection_delta_time
                        start_timestamp_after_irrigation = last_irrigation_timestamp + self.IRRIGATION_DURATION
                        end_timestamp_after_irrigation = start_timestamp_after_irrigation + inspection_delta_time
                       
                        moi_avg_before_irrigation = pandas.read_sql_query(
                            """
                            SELECT  
                                ROUND(AVG(DATA->'$.DATA.CAPACITIVEMOISTURE.MUX0'),0) AS MUX0,
                                ROUND(AVG(DATA->'$.DATA.CAPACITIVEMOISTURE.MUX1'),0) AS MUX1,
                                ROUND(AVG(DATA->'$.DATA.CAPACITIVEMOISTURE.MUX2'),0) AS MUX2,
                                ROUND(AVG(DATA->'$.DATA.CAPACITIVEMOISTURE.MUX3'),0) AS MUX3,
                                ROUND(AVG(DATA->'$.DATA.CAPACITIVEMOISTURE.MUX4'),0) AS MUX4,
                                ROUND(AVG(DATA->'$.DATA.CAPACITIVEMOISTURE.MUX5'),0) AS MUX5,
                                ROUND(AVG(DATA->'$.DATA.CAPACITIVEMOISTURE.MUX6'),0) AS MUX6,
                                ROUND(AVG(DATA->'$.DATA.CAPACITIVEMOISTURE.MUX7'),0) AS MUX7
                            FROM OASIS_DATA
                            WHERE NODE_ID = '{}'
                                    AND  json_length(DATA->'$.DATA.CAPACITIVEMOISTURE') > 0
                                    AND TIMESTAMP >= {}
                                    AND TIMESTAMP < {}
                            ORDER BY TIMESTAMP asc
                            """.format(node, start_timestamp_before_irrigation, end_timestamp_before_irrigation),
                            engine).astype(int)

                        moi_avg_after_irrigation = pandas.read_sql_query(
                            """
                            SELECT  
                                ROUND(AVG(DATA->'$.DATA.CAPACITIVEMOISTURE.MUX0'),0) AS MUX0,
                                ROUND(AVG(DATA->'$.DATA.CAPACITIVEMOISTURE.MUX1'),0) AS MUX1,
                                ROUND(AVG(DATA->'$.DATA.CAPACITIVEMOISTURE.MUX2'),0) AS MUX2,
                                ROUND(AVG(DATA->'$.DATA.CAPACITIVEMOISTURE.MUX3'),0) AS MUX3,
                                ROUND(AVG(DATA->'$.DATA.CAPACITIVEMOISTURE.MUX4'),0) AS MUX4,
                                ROUND(AVG(DATA->'$.DATA.CAPACITIVEMOISTURE.MUX5'),0) AS MUX5,
                                ROUND(AVG(DATA->'$.DATA.CAPACITIVEMOISTURE.MUX6'),0) AS MUX6,
                                ROUND(AVG(DATA->'$.DATA.CAPACITIVEMOISTURE.MUX7'),0) AS MUX7
                            FROM OASIS_DATA
                            WHERE NODE_ID = '{}'
                                    AND  json_length(DATA->'$.DATA.CAPACITIVEMOISTURE') > 0
                                    AND TIMESTAMP >= {}
                                    AND TIMESTAMP < {}
                            ORDER BY TIMESTAMP asc
                            """.format(node, start_timestamp_after_irrigation, end_timestamp_after_irrigation),
                            engine).astype(int)
                        result = ""
                        for mux in MOISTURE_PROBES:
                            diff_moisture = moi_avg_before_irrigation[mux].iloc[0] - moi_avg_after_irrigation[mux].iloc[0]
                            if diff_moisture > 0:
                                result += "✅"
                            elif diff_moisture == 0:
                                result += "⚠️"
                            else:
                                result += "❌"
                    node_name = self.oasis_properties[node]["name"]
                    monitor_message += "{0:10} {1}\n".format(node_name, result)
                    self.logger.info("[inspector] before %s => %s", node_name, moi_avg_before_irrigation)
                    self.logger.info("[inspector]  after %s => %s", node_name, moi_avg_after_irrigation)

            monitor = {}
            monitor["SOURCE"] = "INSPECTOR"
            monitor["MESSAGE"] = monitor_message + "</pre>"
            TelegramAssistantServer.send_monitor_message(monitor)
            self.logger.info("[inspector] ***** ENDING IRRIGATION INSPECTOR *****")
        else:
            self.logger.info(
                "[inspector] Skipping IRRIGATION INSPECTOR due Moisture analytics not found"
            )

    def run_dummy(self):
        ############# get latest moisture analytics result #############
        engine = create_engine(self.SQLALCHEMY_DATABASE_URI)
        analytics = pandas.read_sql_query(
            """
            SELECT TIMESTAMP, DATA
            FROM OASIS_ANALYTIC
            WHERE TYPE='advice'
            ORDER BY TIMESTAMP DESC LIMIT 1
            """,
            engine,
        )
        if not analytics.empty:
            self.logger.info("[irrigation] ***** STARTING DUMMY IRRIGATION *****")

            moisture_analytics_last_calculation = dt.datetime.fromtimestamp(
                int(analytics["TIMESTAMP"].iloc[0])
            ).strftime("%Y-%m-%d %H:%M")
            data = json.loads(analytics["DATA"].iloc[0])
            self.logger.info(
                "[irrigation] Found moisture analytics calculated in: %s",
                moisture_analytics_last_calculation,
            )

            monitor_message = "<b>DUMMY IRRIGATION</b>\n<pre>"
            monitor_message += "<b>Analytics</b>: "+moisture_analytics_last_calculation+"\n"
            monitor_message += "<b>Will rain</b>: "+"Yes" if data["will_rain"] else "No" +"\n<pre>"

            self.logger.info("[irrigation] Weather forecast says it "+"WILL" if data["will_rain"] else "WONT" +" rain")

            nodes_lst = []
            for node in data["node"]:
                advice = data["node"][node]["advice"]
                node_name = self.oasis_properties[node]["name"]
                monitor_message += "{0:10} {1}\n".format(node_name, advice)
                self.logger.info("[irrigation] %s => %s", node_name, advice)

            monitor = {}
            monitor["SOURCE"] = "IRRIGATION"
            monitor["MESSAGE"] = monitor_message + "</pre>"
            TelegramAssistantServer.send_monitor_message(monitor)
            self.logger.info("[irrigation] ***** ENDING DUMMY IRRIGATION *****")
        else:
            self.logger.info(
                "[irrigation] Skipping DUMMY IRRIGATION due Moisture analytics not found"
            )

    def run_smart(self):
        ############# get latest moisture analytics result #############
        engine = create_engine(self.SQLALCHEMY_DATABASE_URI)
        analytics = pandas.read_sql_query(
            """
            SELECT TIMESTAMP, DATA
            FROM OASIS_ANALYTIC
            WHERE TYPE='advice'
            ORDER BY TIMESTAMP DESC LIMIT 1
            """,
            engine,
        )
        if not analytics.empty:
            self.logger.info("[irrigation] ***** STARTING SMART IRRIGATION *****")
            
            moisture_analytics_last_calculation = dt.datetime.fromtimestamp(
                int(analytics["TIMESTAMP"].iloc[0])
            ).strftime("%Y-%m-%d %H:%M")
            data = json.loads(analytics["DATA"].iloc[0])
            self.logger.info(
                "[irrigation] Found moisture analytics calculated in: %s",
                moisture_analytics_last_calculation,
            )
            monitor_message = "<b>SMART IRRIGATION</b>\n"
            monitor_message += "<b>Analytics</b>: "+moisture_analytics_last_calculation+"\n"
            monitor_message += "<b>Will rain</b>: "+"Yes" if data["will_rain"] else "No" +"\n<pre>"

            self.logger.info("[irrigation] Weather forecast says it "+"WILL" if data["will_rain"] else "WONT" +" rain")

            nodes_to_irrigate = []
            nodes_postponed_last_irrigation = []
            nodes_postponed_last_irrigation.extend(
                self.nodes_postponed_to_next_irrigation
            )
            self.nodes_postponed_to_next_irrigation = []

            for node in data["node"]:
                advice = data["node"][node]["advice"]
                node_name = self.oasis_properties[node]["name"]
                monitor_message += "{0:10} {1}\n".format(node_name, advice)
                self.logger.info("[irrigation] advice %s => %s", node_name, advice)
                if advice == "IRRIGATE":
                    if node not in nodes_to_irrigate:
                        nodes_to_irrigate.append(node)
                if advice == "POSTPONE":
                    if node not in nodes_postponed_last_irrigation:
                        self.nodes_postponed_to_next_irrigation.append(node)
                    else:
                        self.logger.info(
                            "[irrigation] postponed before, but it will be irrigate this time => %s",
                            node_name,
                        )
                        nodes_to_irrigate.append(node)

            nodes_df = pandas.DataFrame(nodes_to_irrigate, columns=["NODE_ID"])
            monitor = {}
            monitor["SOURCE"] = "IRRIGATION"
            monitor["MESSAGE"] = monitor_message + "</pre>"
            TelegramAssistantServer.send_monitor_message(monitor)
            self.run(nodes_df)

            self.logger.info("[irrigation] ***** ENDING SMART IRRIGATION *****")
        else:
            self.logger.info(
                "[irrigation] Skipping SMART IRRIGATION due Moisture analytics not found"
            )

    def run_standard(self):
        self.logger.info("[irrigation] ***** STARTING STANDARD IRRIGATION *****")
        ############# get all alive nodes but not in quarantine #############
        now = int(time.time())
        period_for_last_heartbeat = int(now - HEARTBEAT_PERIOD)
        engine = create_engine(self.SQLALCHEMY_DATABASE_URI)
        nodes = pandas.read_sql_query(
            """
            SELECT NODE_ID
            FROM OASIS_HEARTBEAT
            WHERE LAST_UPDATE >= {}
            AND QUARANTINE <> 1
            """.format(
                period_for_last_heartbeat
            ),
            engine,
        )

        monitor_msg = {
            "irrigation": {
                "mode": "standard",
                "duration": self.IRRIGATION_DURATION,
                "nodes": nodes["NODE_ID"].values.tolist(),
                "status": "started",
            }
        }
        self.socketio.emit("ws-server-monitor", data=monitor_msg)
        self.run(nodes)
        monitor_msg["irrigation"]["status"] = "finished"

        self.socketio.emit("ws-server-monitor", data=monitor_msg)

        self.logger.info("[irrigation] ***** ENDING STANDARD IRRIGATION *****")

    def run(self, nodes):
        nodes_to_irrigate = len(nodes.index)
        self.logger.info("[irrigation] %d nodes will receive water.", nodes_to_irrigate)

        if nodes_to_irrigate > 0:

            if self.cfg["WATER_TANK"]["MODE"] == "support" :
                message = json.dumps(
                    {
                        "NODE_ID": self.cfg["WATER_TANK"]["NODE_MANAGER"],
                        "MESSAGE_ID": "water_sched_init",
                        "COMMAND": {"SWITCH_B": True},
                    }
                )
                self.logger.info("[irrigation] water tank message >=> %s", message)
                self.mqtt.publish(self.cfg["MQTT"]["SUPPORT_TOPIC_INBOUND"], message)
            else:
                url = "http://%s/water-tank" % (self.cfg["WATER_TANK"]["SERVER"])
                headers = {"Content-type": "application/json"}
                response = requests.post(
                    url,
                    data=json.dumps({"DIRECTION": "OUT", "ACTION": True}),
                    headers=headers,
                )
                self.logger.info("[irrigation]  Water tank server response: %s", response)

                if response.status_code != 200:
                    self.logger.info(
                        "[irrigation] Water Tank connection http status code: %s!!!",
                        str(response.status_code),
                    )

            ### WARM-UP
            if self.cfg["IRRIGATION"]["WARMUP"]:
                self.logger.info("[irrigation] starting warm-up")
                for index, node in nodes.iterrows():
                    message = json.dumps(
                        {
                            "NODE_ID": node["NODE_ID"],
                            "MESSAGE_ID": "water_sched_warmup",
                            "COMMAND": {"WATER": True},
                        }
                    )
                    self.logger.info("[irrigation] warm-up >=> %s", message)
                    self.mqtt.publish(self.cfg["MQTT"]["OASIS_TOPIC_INBOUND"], message)
                    time.sleep(5)

                time.sleep(self.IRRIGATION_DURATION / 2)
                message = json.dumps(
                    {
                        "NODE_ID": "ALL",
                        "MESSAGE_ID": "water_sched_warmup",
                        "COMMAND": {"WATER": False},
                    }
                )
                self.mqtt.publish(self.cfg["MQTT"]["OASIS_TOPIC_INBOUND"], message)
                self.logger.info("[irrigation] ending warm-up")
            else:
                self.logger.info("[irrigation] warm-up disabled")

            node_id = None
            for index, node in nodes.iterrows():
                node_id = node["NODE_ID"]
                message = json.dumps(
                    {
                        "NODE_ID": str(node_id),
                        "MESSAGE_ID": "water_sched",
                        "COMMAND": {"WATER": True},
                    }
                )
                self.logger.info("[irrigation] %s", message)
                self.mqtt.publish(self.cfg["MQTT"]["OASIS_TOPIC_INBOUND"], message)
                time.sleep(self.IRRIGATION_DURATION)
                # message = json.dumps({'NODE_ID': str(node_id), 'MESSAGE_ID':"water_sched", 'COMMAND':{"WATER": False}})
                message = json.dumps(
                    {
                        "NODE_ID": "ALL",
                        "MESSAGE_ID": "water_sched",
                        "COMMAND": {"WATER": False},
                    }
                )
                self.mqtt.publish(self.cfg["MQTT"]["OASIS_TOPIC_INBOUND"], message)
                self.logger.info("[irrigation] %s", message)

            message = json.dumps(
                {
                    "NODE_ID": "ALL",
                    "MESSAGE_ID": "water_sched",
                    "COMMAND": {"WATER": False},
                }
            )
            self.logger.info("[irrigation] %s", message)
            self.mqtt.publish(self.cfg["MQTT"]["OASIS_TOPIC_INBOUND"], message)

            if self.cfg["WATER_TANK"]["MODE"] == "support" :
                message = json.dumps(
                    {
                        "NODE_ID": self.cfg["WATER_TANK"]["NODE_MANAGER"],
                        "MESSAGE_ID": "water_sched_end",
                        "COMMAND": {"SWITCH_B": False},
                    }
                )
                self.logger.info("[irrigation] water tank message >=> %s", message)
                self.mqtt.publish(self.cfg["MQTT"]["SUPPORT_TOPIC_INBOUND"], message)
            else:
                requests.post(
                    url,
                    data=json.dumps({"DIRECTION": "OUT", "ACTION": False}),
                    headers=headers,
                )
        else:
            self.logger.info("[irrigation] skip irrigation procedures")


if __name__ == "__main__":
    print("*** STARTING Irrigation Test ***")
    app = Irrigation()
    app.monitorTankLevel()
    while True:
        time.sleep(3)
        print("*")
