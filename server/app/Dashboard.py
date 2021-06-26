#!/usr/bin/python3
# -*- coding: utf-8 -*-
import datetime as dt
import os
import glob
import time
import requests


class Dashboard:
    HEARTBEAT_PERIOD = 15000 / 1000  # seconds

    def __init__(self, logger, cfg):
        self.logger = logger
        self.cfg = cfg

    def weather_currently(self):
        time_start = dt.datetime.now()

        weather_key = self.cfg["WEATHER_KEY"]
        lat = self.cfg["LATITUDE"]
        long = self.cfg["LONGITUDE"]
        try:
            response = requests.get(
                "https://api.forecast.io/forecast/%s/%s,%s?units=si&lang=pt&exclude=flags,hourly,daily"
                % (weather_key, lat, long)
            )
            data = response.json()
            weather = data["currently"]
        except requests.ConnectionError:
            self.logger.debug("[Dashboard > Weather] ConnectionError!!!")
            weather = {}
            weather["icon"] = "none"
            weather["summary"] = "Offline"
            weather["apparentTemperature"] = 00.00
            weather["humidity"] = 0.00
            weather["precipProbability"] = 0.00
            weather["precipIntensity"] = 0.0000
            weather["windSpeed"] = 0.00

        time_end = dt.datetime.now()
        elapsed_time = time_end - time_start
        self.logger.debug(
            "[Dashboard > Weather] took %s secs", elapsed_time.total_seconds()
        )

        return weather

    def raspberrypi(self):
        time_start = dt.datetime.now()
        data = {}
        data["cpu_temp"] = self.__cpu_temperature()
        data["mem_usage"] = self.__memory_usage()
        data["disk_usage"] = self.__disk()
        data["processes"] = self.__processes()
        data["sys_load"] = self.__system_load()

        time_end = dt.datetime.now()
        elapsed_time = time_end - time_start
        self.logger.debug(
            "[Dashboard > Rasp] took %s secs", elapsed_time.total_seconds()
        )

        return data

    def farm(self, modules):
        time_start = dt.datetime.now()

        temperature = 0
        humidity = 0
        number_dht = 0
        data = {}
        for module in modules:
            node_data = module.data()
            dht = node_data.get("DHT")
            soil = node_data.get("CAPACITIVEMOISTURE")
            if dht:
                temperature += int(dht.get("TEMPERATURE"))
                humidity += int(dht.get("HUMIDITY"))
                number_dht = number_dht + 1
            if soil:
                # {'MUX0': 382, 'MUX1': 354, 'MUX2': 345, 'MUX3': 672, 'MUX4': 27,
                # 'MUX5': 25, 'MUX6': 26, 'MUX7': 26}
                # TODO: put some brain in here
                print(soil)
        data["humidity"] = int(humidity / number_dht) if number_dht > 0 else 0
        data["temperature"] = int(temperature / number_dht) if number_dht > 0 else 0
        data["soil"] = 0

        time_end = dt.datetime.now()
        elapsed_time = time_end - time_start
        self.logger.debug(
            "[Dashboard > Farm] took %s secs", elapsed_time.total_seconds()
        )
        return data

    def nodes(self, latest_beat):
        time_start = dt.datetime.now()

        offline = 0
        online = 0
        now = int(time.time())

        for node in latest_beat:
            diff = now - int(node[0])
            if diff > self.HEARTBEAT_PERIOD * 2:  # OMG lost 2 heartbeats ?
                offline = offline + 1
            else:
                online = online + 1

        data = {}
        data["online_count"] = online
        data["offline_count"] = offline

        time_end = dt.datetime.now()
        elapsed_time = time_end - time_start
        self.logger.debug(
            "[Dashboard > Nodes] took %s secs", elapsed_time.total_seconds()
        )
        return data

    def __cpu_temperature(self):
        time_start = dt.datetime.now()

        cpu_temp = -1
        try:
            f = open("/sys/class/thermal/thermal_zone0/temp")
            cpu_temp = f.read()
            f.close()
        except IOError as e:
            print("[DASHBOARD] cpu temperature I/O error")
        response = int((int(cpu_temp) / 1000.0))

        time_end = dt.datetime.now()
        elapsed_time = time_end - time_start
        self.logger.debug(
            "[Dashboard > CPU Temp] took %s secs", elapsed_time.total_seconds()
        )
        return response

    def __memory_usage(self):
        time_start = dt.datetime.now()

        items = {}
        mem_usage = -1
        try:
            for l in open("/proc/meminfo").readlines():
                a = l.split()
                items[a[0]] = int(a[1])
            mem_usage = int(
                (100 - 100.0 * items["MemAvailable:"] / (items["MemTotal:"] or 1))
            )
        except IOError as e:
            print("[DASHBOARD] memory usage I/O error")

        time_end = dt.datetime.now()
        elapsed_time = time_end - time_start
        self.logger.debug(
            "[Dashboard > Mem Usage] took %s secs", elapsed_time.total_seconds()
        )
        return mem_usage

    def __disk(self):
        time_start = dt.datetime.now()

        statfs = os.statvfs("/")
        response = int((100 - 100.0 * statfs.f_bavail / statfs.f_blocks))
        time_end = dt.datetime.now()
        elapsed_time = time_end - time_start
        self.logger.debug(
            "[Dashboard > Disk] took %s secs", elapsed_time.total_seconds()
        )
        return response

    def __processes(self):
        time_start = dt.datetime.now()
        response = len(glob.glob("/proc/[0-9]*"))
        time_end = dt.datetime.now()
        elapsed_time = time_end - time_start
        self.logger.debug(
            "[Dashboard > System Load] took %s secs", elapsed_time.total_seconds()
        )
        return response

    def __system_load(self):
        time_start = dt.datetime.now()
        sys_load = -1
        try:
            f = open("/proc/loadavg")
            sys_load = float(f.read().split()[1])
        except IOError as e:
            print("[DASHBOARD] system load I/O error")
        time_end = dt.datetime.now()
        elapsed_time = time_end - time_start
        self.logger.debug(
            "[Dashboard > System Load] took %s secs", elapsed_time.total_seconds()
        )
        return sys_load
