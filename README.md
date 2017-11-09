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
nodemcu-uploader upload apps.lua credentials.lua init.lua
nodemcu-uploader terminal
node.restart()
dofile("apps.lua")
```

### .credentials file
```lua
SSID = "YOUR SSID"
PASSWORD = "YOUR PASSWORD"
```
