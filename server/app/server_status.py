#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys,os,time,posix,glob

def cputemp():
  f = open("/sys/class/thermal/thermal_zone0/temp")
  CPUTemp = f.read()
  f.close()
  StringToOutput= str(int(CPUTemp)/1000.0)
  return StringToOutput



def proc_meminfo():
  items = {}
  for l in open('/proc/meminfo').readlines():
    a = l.split()
    items[a[0]] = int(a[1])
  # print items['MemTotal:'], items['MemFree:'], items['SwapTotal:'], items['SwapFree:']
  return items

loadav = float(open("/proc/loadavg").read().split()[1])
processes = len(glob.glob('/proc/[0-9]*'))
statfs = os.statvfs('/')
rootperc = 100-100.*statfs.f_bavail/statfs.f_blocks
temp = cputemp()
meminfo = proc_meminfo()
memperc = "%d%%" % (100-100.*meminfo['MemFree:']/(meminfo['MemTotal:'] or 1))
swapperc = "%d%%" % (100-100.*meminfo['SwapFree:']/(meminfo['SwapTotal:'] or 1))


print ("  Temperature: ",temp)
print ("  System load: ",loadav)
print ("  Disk: ",rootperc)
print ("  Processes: ", processes)
print ("  Memory usage: ", memperc)
print ("  Swap usage: ", swapperc)

sys.exit(0)
