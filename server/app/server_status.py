#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys,os,glob

def cputemp():
  f = open("/sys/class/thermal/thermal_zone0/temp")
  CPUTemp = f.read()
  f.close()
  return "%dC" % (int(CPUTemp)/1000.0)

def meminfo():
  items = {}
  for l in open('/proc/meminfo').readlines():
    a = l.split()
    items[a[0]] = int(a[1])
  return "%d%%" % (100-100.*items['MemFree:']/(items['MemTotal:'] or 1))

def disk():
  items = {}
  statfs = os.statvfs('/')
  return "%d%%" % (100-100.*statfs.f_bavail/statfs.f_blocks)

def processes():
  return len(glob.glob('/proc/[0-9]*'))

def system_load():
  return float(open("/proc/loadavg").read().split()[1])


print ("  Temperature: ",cputemp())
print ("  System load: ",system_load())
print ("  Disk: ",disk())
print ("  Processes: ", processes())
print ("  Memory usage: ", meminfo())

sys.exit(0)
