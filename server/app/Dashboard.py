#!/usr/bin/python3
# -*- coding: utf-8 -*-
import requests,sys,os,glob,json

class Dashboard:
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

    def cpu_temperature(self):
      f = open("/sys/class/thermal/thermal_zone0/temp")
      CPUTemp = f.read()
      f.close()
      return "%d°C" % (int(CPUTemp)/1000.0)

    def memory_usage(self):
      items = {}
      for l in open('/proc/meminfo').readlines():
        a = l.split()
        items[a[0]] = int(a[1])
      return "%d%%" % (100-100.*items['MemAvailable:']/(items['MemTotal:'] or 1))

    def disk(self):
      items = {}
      statfs = os.statvfs('/')
      return "%d%%" % (100-100.*statfs.f_bavail/statfs.f_blocks)

    def processes(self):
      return len(glob.glob('/proc/[0-9]*'))

    def system_load(self):
      return float(open("/proc/loadavg").read().split()[1])
