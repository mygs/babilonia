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
#define BUILD_DATE       "20180116"
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
module.SSID = "SSID"
module.PASSWORD = "PASSWD"

-- MQTT configs
module.BROKER = "BROKER IP" --nabucodonasor
module.PORT = 1883 -- mosquitto default port
module.MQTT_STATUS = 1 -- 0 Connected / 1 = Disconnected

module.SLEEP_TIME = 4 -- seconds

module.SYNC_CLOCK_SERVER = "pool.ntp.br"
-- I/O ports
module.PIN_DHT   = 5
module.PIN_FAN   = 6
module.PIN_LIGHT = 7
module.PIN_ANALOGIC_MOISTURE = 0

-- default values
module.TEMPERATURE_THRESHOLD = 25 -- above this temperature, fan should be off
module.TEMPERATURE_NSAMPLES = 10
module.TEMPERATURE_SMA = 25 -- Simple Moving Average Temperature
-- https://crontab.guru/ (nodemcu time is GMT. Sao Paulo time is GMT-2)
module.MASK_CRON_LIGHT_ON="0 11 * * *"  -- 9AM SP time (LocalTime+2H)
module.MASK_CRON_LIGHT_OFF="0 20 * * *" -- 6PM SP time (LocalTime+2H)
module.MASK_CRON_CTRL="* * * * *" -- At every minute

-- overwrite variables
if file.exists("nconfig.lua") then
  dofile("nconfig.lua")
end

print("TEMPERATURE_THRESHOLD:"..module.TEMPERATURE_THRESHOLD)
print("MASK_CRON_LIGHT_ON:"..module.MASK_CRON_LIGHT_ON)
print("MASK_CRON_LIGHT_OFF:"..module.MASK_CRON_LIGHT_OFF)
print("MASK_CRON_CTRL:"..module.MASK_CRON_CTRL)


```
### mqtt reference
https://nodemcu.readthedocs.io/en/master/en/modules/mqtt/#mqttclient

https://www.foobarflies.io/a-simple-connected-object-with-nodemcu-and-mqtt/

http://wingsquare.com/blog/setting-up-mqtt-mosquitto-broker-in-ubuntu-linux/

### python imports
```
sudo pip install paho-mqtt
sudo pip install sqlalchemy
sudo pip install flask-mysql
sudo pip install flask-socketio
sudo pip3 install flask-mqtt
```

### middlwares & tools
```
sudo apt-get install mysql-server && sudo apt-get install mysql-client
sudo apt-get install dos2unix
sudo apt-get install python3-mysqldb
```

### mqtt commands

subscribe all topics
```
mosquitto_sub -h 192.168.1.60 -t "#" -v
```
send message
```
mosquitto_pub -h 192.168.1.60 -t "/cfg" -m "fan:1;light:1;temp:24"
mosquitto_pub -h 192.168.1.60 -t "/cfg" -m "id:3765036;fan:1;light:1;temp:24"
mosquitto_pub -h 192.168.1.60 -t "/cfg" -m "mclon:0 7 * * *;mcloff:0 7 * * *;mcctrl:*/7 * * * *"
mosquitto_pub -h 192.168.1.60 -t "/cfg" -m "id:3765036;mclon:0 7 * * *;mcloff:0 7 * * *;mcctrl:*/2 * * * *"
mosquitto_pub -h 192.168.1.60 -t "/cfg" -m "id:3765036;cmd:3"
mosquitto_pub -h 192.168.1.60 -t "/online" -m "id:3765036;rb:0"


```

### database administration
```bash

```

### config.json template
```
{
    "db":{
        "host":"HOST",
        "user":"USER",
        "password":"PASSWORD",
        "schema":"SCHEMA"
    },
    "mqtt":{
        "broker":"HOST",
        "port":PORT,
        "keepalive":TIME
    }
}

```

### daemon
http://blog.scphillips.com/posts/2013/07/getting-a-python-script-to-run-in-the-background-as-a-service-on-boot/

```bash
dos2unix nabucodonosor.sh
sudo chmod 755 nabucodonosor.py
sudo chmod 755 nabucodonosor.sh
sudo cp nabucodonosor.sh /etc/init.d
sudo update-rc.d nabucodonosor.sh defaults
sudo /etc/init.d/nabucodonosor.sh start
sudo /etc/init.d/nabucodonosor.sh status
```
