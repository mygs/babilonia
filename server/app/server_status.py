import sys,os,time,posix,glob,utmp

def cputemp():
  f = open("/sys/class/thermal/thermal_zone0/temp")
  CPUTemp = f.read()
  f.close()
  StringToOutput= str(int(CPUTemp)/1000.0)
  return StringToOutput


def utmp_count():
  u = utmp.UtmpRecord()
  users = 0
  for i in u:
    if i.ut_type == utmp.USER_PROCESS: users += 1
  return users

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
users = utmp_count()
temp = cputemp()
meminfo = proc_meminfo()
memperc = "%d%%" % (100-100.*meminfo['MemFree:']/(meminfo['MemTotal:'] or 1))
swapperc = "%d%%" % (100-100.*meminfo['SwapFree:']/(meminfo['SwapTotal:'] or 1))


print "  Temperature:  %s" % (temp)
print "  System load:  %-5.2f" % (loadav)
print "  Disk: %.1f%%"% (rootperc)
print "  Processes: %d "% (processes)
print "  Users logged in: %d" % (users)
print "  Memory usage: %-4s" % (memperc)
print "  Swap usage: %s" % (swapperc)

sys.exit(0)
