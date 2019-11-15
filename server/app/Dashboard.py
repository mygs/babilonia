#!/usr/bin/python3
# -*- coding: utf-8 -*-
import requests,sys,os,glob,json,time

class Dashboard:
    HEARTBEAT_PERIOD=15000/1000 #seconds

    def __init__(self, cfg):
        self.cfg = cfg

    def weather_currently(self):
        weather_key = self.cfg["WEATHER_KEY"]
        lat = self.cfg["LATITUDE"]
        long = self.cfg["LONGITUDE"]
        response = requests.get('https://api.forecast.io/forecast/%s/%s,%s?units=si&lang=pt&exclude=flags,hourly,daily'%(
                                    weather_key, lat, long))
        data = response.json()
        return data['currently']

    def raspberrypi(self):
      data = {}
      data['cpu_temp']=self.__cpu_temperature()
      data['mem_usage']=self.__memory_usage()
      data['disk_usage']=self.__disk()
      data['processes']=self.__processes()
      data['sys_load']=self.__system_load()
      return data

    def nodes(self, latest_beat):
      offline = 0
      online = 0
      now = int(time.time())
      for node in latest_beat:
          diff = now - int(node[0])
          if diff > self.HEARTBEAT_PERIOD:
              offline = offline + 1
          else:
              online = online + 1

      data = {}
      data['online']=online
      data['offline']=offline
      return data

    def __cpu_temperature(self):
      f = open("/sys/class/thermal/thermal_zone0/temp")
      CPUTemp = f.read()
      f.close()
      return int((int(CPUTemp)/1000.0))

    def __memory_usage(self):
      items = {}
      for l in open('/proc/meminfo').readlines():
        a = l.split()
        items[a[0]] = int(a[1])
      return int((100-100.*items['MemAvailable:']/(items['MemTotal:'] or 1)))

    def __disk(self):
      items = {}
      statfs = os.statvfs('/')
      return int((100-100.*statfs.f_bavail/statfs.f_blocks))

    def __processes(self):
      return len(glob.glob('/proc/[0-9]*'))

    def __system_load(self):
      return float(open("/proc/loadavg").read().split()[1])
