#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os, time, json, requests
import datetime as dt
from TelegramAssistantServer import *


class Watchdog:
    def __init__(self, logger, cfg, oasis_properties):
        self.logger = logger
        self.cfg = cfg
        self.oasis_properties = oasis_properties
        self.nodes = self.initialise_node_cache()
        self.servers = self.initialise_server_cache()
        self.water_tank_is_online = True

    def initialise_node_cache(self):
        result = {}
        for node in self.oasis_properties:
            if node != "oasis-undefined":
                result[node] = {"ONLINE": True, "IRRIGATION": True}
        return result

    def initialise_server_cache(self):
        result = {}
        for server in self.cfg["WATCHDOG"]["SERVERS"]:
            result[server] = {"ONLINE": True}
        return result

    def run(self):
        self.logger.info("[watchdog]  ***** STARTING WATCHDOG *****")
        self.run_servers()
        self.run_status()
        self.run_water()
        self.run_water_tank_node_status()


    def run_water_tank_node_status(self):
        now = int(time.time())
        offline = int(now - self.cfg["WATCHDOG"]["OFFLINE_TIME"])
        engine = create_engine(self.cfg["SQLALCHEMY_DATABASE_URI"])
        water_tank_status_db = pandas.read_sql_query(
            """
            SELECT COUNT(*) AS IS_OFFLINE
            FROM SUPPORT
            WHERE TIMESTAMP < {}
            AND TYPE = 'WATER_TANK' 
            """.format( offline),
            engine,
        )
        is_current_offline = True if not water_tank_status_db.empty and water_tank_status_db["IS_OFFLINE"].iloc[0] > 0 else False

        monitor = {}
        monitor["SOURCE"] = "WATCHDOG"
        if is_current_offline:
            if self.water_tank_is_online:
                monitor["MESSAGE"] = "❌ Water Tank node ficou <b>OFFLINE</b>"
                TelegramAssistantServer.send_monitor_message(message)
                self.water_tank_is_online = False
            else:
                self.logger.info("[watchdog] Water Tank node still offline")
        else:
            if not self.water_tank_is_online:
                monitor["MESSAGE"] = "✅ Water Tank node voltou a ficar <b>ONLINE</b>"
                self.water_tank_is_online = True
            else:
                self.logger.debug("[watchdog] Water Tank node still online")

    def run_water(self):
        now = int(time.time())
        irrigation_window_time = int(now - self.cfg["WATCHDOG"]["INTERVAL"])
        number_of_sample_water_on = int(
            self.cfg["WATCHDOG"]["IRRIGATION_DURATION"] / 30
        )
        engine = create_engine(self.cfg["SQLALCHEMY_DATABASE_URI"])
        for cache_node_id in self.nodes:
            water_data = pandas.read_sql_query(
                """
                SELECT IFNULL(sum(DATA->'$.DATA.WATER'=1),0) as WATER_ON_DATA,
                       COUNT(*) as TOTAL_DATA
                FROM OASIS_DATA
                WHERE NODE_ID = '{}'
                      AND TIMESTAMP >= {}
                """.format(
                    cache_node_id, irrigation_window_time
                ),
                engine,
            )
            oasis_name = self.oasis_properties[cache_node_id]["name"]
            water_on_data = int(water_data.WATER_ON_DATA.iat[0])
            total_data = int(water_data.TOTAL_DATA.iat[0])
            self.logger.info(
                "[watchdog] %s > total_data: %d, water_on_data: %d",
                oasis_name,
                total_data,
                water_on_data,
            )
            if total_data > 0 and (
                (total_data == water_on_data)
                or (water_on_data >= number_of_sample_water_on)
            ):
                oasis_tot_water_on_min = int(
                    self.cfg["WATCHDOG"]["IRRIGATION_DURATION"] / 60
                )
                window = int(self.cfg["WATCHDOG"]["INTERVAL"] / 60)
                monitor_message = "⚠️ <b>" + oasis_name + "</b> irrigou por mais de "
                monitor_message += str(oasis_tot_water_on_min) + " minutos nos últimos "
                monitor_message += str(window) + " minutos\n"
                monitor = {}
                monitor["SOURCE"] = "WATCHDOG"
                monitor["MESSAGE"] = monitor_message
                TelegramAssistantServer.send_monitor_message(monitor)

    def run_status(self):
        now = int(time.time())
        offline = int(now - self.cfg["WATCHDOG"]["OFFLINE_TIME"])
        engine = create_engine(self.cfg["SQLALCHEMY_DATABASE_URI"])
        offline_nodes = pandas.read_sql_query(
            """
            SELECT NODE_ID
            FROM OASIS_HEARTBEAT
            WHERE LAST_UPDATE < {}
            AND QUARANTINE <> 1
            """.format(
                offline
            ),
            engine,
        )
        offline_nodes_id = []
        for index, offline_node in offline_nodes.iterrows():
            offline_node_id = offline_node["NODE_ID"]
            offline_nodes_id.append(offline_node_id)
        offline_str = dt.datetime.fromtimestamp(offline).strftime("%Y-%m-%d %H:%M:%S")
        self.logger.info(
            "[watchdog] found %d nodes offline. No response since %s",
            len(offline_nodes_id),
            offline_str,
        )

        status_change_nodes_offline = []
        status_change_nodes_online = []

        for cache_node_id in self.nodes:
            cache_node = self.nodes[cache_node_id]
            cache_node_name = self.oasis_properties[cache_node_id]["name"]
            if cache_node_id in offline_nodes_id:
                if cache_node["ONLINE"] == True:
                    status_change_nodes_offline.append(cache_node_name)
                    cache_node["ONLINE"] = False
                else:
                    self.logger.info("[watchdog] %s still offline", cache_node_name)
            else:
                if cache_node["ONLINE"] == False:
                    status_change_nodes_online.append(cache_node_name)
                    cache_node["ONLINE"] = True
        monitor_message = ""
        publish = False
        if status_change_nodes_offline:
            time_string = str(int(self.cfg["WATCHDOG"]["OFFLINE_TIME"] / 60))
            monitor_message += "❌ Oasis <b>OFFLINE</b>: "
            monitor_message += ", ".join(map(str, status_change_nodes_offline))
            monitor_message += " por mais de " + time_string + " minutos\n"
            publish = True
        if status_change_nodes_online:
            monitor_message += "✅ Voltaram a ficar <b>ONLINE</b>: "
            monitor_message += ", ".join(map(str, status_change_nodes_online))
            monitor_message += "\n"
            publish = True
        if publish:
            monitor = {}
            monitor["SOURCE"] = "WATCHDOG"
            monitor["MESSAGE"] = monitor_message
            TelegramAssistantServer.send_monitor_message(monitor)


    def run_servers(self):
        change_status_servers_offline = []
        change_status_servers_online = []
        monitor_message = ""

        for ip in self.servers:
            host_up  = True if os.system("ping -c 1 " + ip) is 0 else False
            server = self.servers[ip]
            if host_up != server["ONLINE"]:
                if host_up:
                    change_status_servers_online.append(ip)
                else:
                    change_status_servers_offline.append(ip)

                server["ONLINE"] = host_up
                self.logger.info(
                    "[watchdog] server %s changed its status to %s",
                    ip,
                    "ONLINE" if host_up else "OFFLINE"
                )
        publish = False
        if change_status_servers_offline:
            monitor_message += "❌ Servidores ficaram <b>OFFLINE</b>: "
            monitor_message += ", ".join(map(str, change_status_servers_offline))
            monitor_message += "\n"
            publish = True
        if change_status_servers_online:
            monitor_message += "✅ Servidores voltaram a ficar <b>ONLINE</b>: "
            monitor_message += ", ".join(map(str, change_status_servers_online))
            monitor_message += "\n"
            publish = True

        if publish:
            monitor = {}
            monitor["SOURCE"] = "WATCHDOG"
            monitor["MESSAGE"] = monitor_message
            TelegramAssistantServer.send_monitor_message(monitor)
        else:
            self.logger.info(
                "[watchdog] all servers keep previous status"
            )

if __name__ == "__main__":
    SERVER_HOME = os.path.dirname(os.path.abspath(__file__))
    COMMON_DIR = os.path.join(SERVER_HOME, "../../common")
    os.chdir(SERVER_HOME)  # change directory because of log files
    with open(os.path.join(SERVER_HOME, "config.json"), "r") as config_json_file:
        cfg = json.load(config_json_file)

    with open(
        os.path.join(COMMON_DIR, "oasis_properties.json"), "r"
    ) as oasis_prop_file:
        oasis_properties = json.load(oasis_prop_file)

    with open(os.path.join(SERVER_HOME, "logging.json"), "r") as logging_json_file:
        logging.config.dictConfig(json.load(logging_json_file))
        logger = logging.getLogger(__name__)

    watchdog = Watchdog(logger, cfg, oasis_properties)

    watchdog.run()
