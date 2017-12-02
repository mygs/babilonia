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
#ifdef DEVELOP_VERSION

/*/app/include/user_modules.h*/
#define LUA_USE_MODULES_CRON
#define LUA_USE_MODULES_DHT
#define LUA_USE_MODULES_PWM
#define LUA_USE_MODULES_RTCTIME
#define LUA_USE_MODULES_SNTP

/*app/include/user_version.h*/
#define NODE_VERSION   "NodeMCU 2.1.0 babilonia"
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
-- Credentials
SSID = "THE WIRELESS SSID"
PASSWORD = "THE WIRELESS PASSWORD"
-- General configurations
NODEID = "THE NODE ID"

DATAREPO = "THE URL"


if file.exists("mask-cron.lua") then
  dofile("mask-cron.lua")
  file.remove("mask-cron.lua")
else
  -- https://crontab.guru/ (nodemcu time is GMT. Sao Paulo time is GMT-2)
  MASK_CRON_LIGHT_ON="0 11 * * *"  -- 9AM SP time (LocalTime+2H)
  MASK_CRON_LIGHT_OFF="0 20 * * *" -- 6PM SP time (LocalTime+2H)
  MASK_CRON_CTRL="* * * * *" -- At every minute
end
print("MASK_CRON_LIGHT_ON:"..MASK_CRON_LIGHT_ON)
print("MASK_CRON_LIGHT_OFF:"..MASK_CRON_LIGHT_OFF)
print("MASK_CRON_CTRL:"..MASK_CRON_CTRL)

-- default values
TEMPERATURE_NSAMPLES = 10
TEMPERATURE_SMA = 25 -- Simple Moving Average Temperature
TEMPERATURE_THRESHOLD = 25 -- above this temperature, fan should be off

PIN_DHT   = 5
PIN_FAN   = 6
PIN_LIGHT = 7

RATIO_CTRL_UPDATE_UPLOAD = 4 -- X/Y: For each X update, execute Y upload
```
