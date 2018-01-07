# babilonia

### esp-open-sdk (to build firmware)
```bash
git clone --recursive https://github.com/pfalcon/esp-open-sdk
export PATH="/data/github/esp-open-sdk/xtensa-lx106-elf/bin/:$PATH"
alias xgcc="xtensa-lx106-elf-gcc"
```
### nodemcu-firmware

```bash
git clone --recursive https://github.com/nodemcu/nodemcu-firmware.git
```

```c
/*app/include/user_config.h*/
//#define CLIENT_SSL_ENABLE
//#define SHA2_ENABLE

/*/app/include/user_modules.h*/
#define LUA_USE_MODULES_CRON
#define LUA_USE_MODULES_DHT
#define LUA_USE_MODULES_FILE
#define LUA_USE_MODULES_GPIO
#define LUA_USE_MODULES_MQTT
#define LUA_USE_MODULES_NET
#define LUA_USE_MODULES_RTCTIME
#define LUA_USE_MODULES_SNTP
#define LUA_USE_MODULES_TMR
#define LUA_USE_MODULES_WIFI

/*app/include/user_version.h*/
#define NODE_VERSION   "NodeMCU 2.1.2 babilonia"
#define BUILD_DATE       "20171016"
```bash


### flash firmware
```bash
esptool.py --port /dev/ttyUSB0 write_flash -fm dio 0x00000 0x00000.bin 0x10000 0x10000.bin
```

### command
https://github.com/kmpm/nodemcu-uploader/blob/master/doc/USAGE.md
```bash
nodemcu-uploader node restart
nodemcu-uploader file list
nodemcu-uploader file remove *
nodemcu-uploader upload apps.lua config.lua init.lua
nodemcu-uploader terminal
node.restart()
dofile("apps.lua")
```
### cross compiling
```bash
./luac.cross -o config.lc config.lua
./luac.cross -o apps.lc apps.lua
nodemcu-uploader file remove *
nodemcu-uploader upload apps.lc config.lc init.lua
```

### config.lua file
```lua
module = {}
-- Wifi Credentials
module.SSID = "THE SSID"
module.PASSWORD = "THE PASSWORD"

-- MQTT configs
module.BROKER = "BROKER IP"
module.PORT = 1883 -- mosquitto default port
module.MQTT_STATUS = 1 -- 0 Connected / 1 = Disconnected

module.SLEEP_TIME = 4 -- seconds

-- schedules
if file.exists("mask-cron.lua") then
  dofile("mask-cron.lua")
  file.remove("mask-cron.lua")
else
  -- https://crontab.guru/ (nodemcu time is GMT. Sao Paulo time is GMT-2)
  -- default values
  module.MASK_CRON_LIGHT_ON="0 11 * * *"  -- 9AM SP time (LocalTime+2H)
  module.MASK_CRON_LIGHT_OFF="0 20 * * *" -- 6PM SP time (LocalTime+2H)
  module.MASK_CRON_CTRL="* * * * *" -- At every minute
end
print("MASK_CRON_LIGHT_ON:"..module.MASK_CRON_LIGHT_ON)
print("MASK_CRON_LIGHT_OFF:"..module.MASK_CRON_LIGHT_OFF)
print("MASK_CRON_CTRL:"..module.MASK_CRON_CTRL)

-- default values
module.TEMPERATURE_NSAMPLES = 10
module.TEMPERATURE_SMA = 25 -- Simple Moving Average Temperature
module.TEMPERATURE_THRESHOLD = 25 -- above this temperature, fan should be off

-- I/O ports
module.PIN_DHT   = 5
module.PIN_FAN   = 6
module.PIN_LIGHT = 7
```
### mqtt reference
https://nodemcu.readthedocs.io/en/master/en/modules/mqtt/#mqttclient
https://www.foobarflies.io/a-simple-connected-object-with-nodemcu-and-mqtt/
http://wingsquare.com/blog/setting-up-mqtt-mosquitto-broker-in-ubuntu-linux/
