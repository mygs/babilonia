# babilonia

### Env variables
/etc/profile.d/00-babilonia.sh
```bash
PATH=$PATH:/data/github/esp-open-sdk/xtensa-lx106-elf/bin
alias xgcc="xtensa-lx106-elf-gcc"
export BABILONIA_HOME=/data/github/babilonia
```
### USB rule
/etc/udev/rules.d/babilonia.rules

```bash
SUBSYSTEM=="usb", ACTION=="add", ENV{DEVTYPE}=="usb_device", ENV{ID_VENDOR}=="1a86", RUN+="/babilonia/utils/nodeupdate.sh"
```

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

#### nodemcu-firmware customisation

app/include/user_config.h
```c
//#define CLIENT_SSL_ENABLE
//#define SHA2_ENABLE
```

/app/include/user_modules.h
```c
//#define LUA_USE_MODULES_ADC
//#define LUA_USE_BUILTIN_COROUTINE
//#define LUA_USE_BUILTIN_MATH
//#define LUA_USE_BUILTIN_DEBUG_MINIMAL
//#define LUA_USE_MODULES_BIT
#define LUA_USE_MODULES_CRON
//#define LUA_USE_MODULES_I2C
#define LUA_USE_MODULES_DHT
#define LUA_USE_MODULES_FILE
#define LUA_USE_MODULES_GPIO
#define LUA_USE_MODULES_MQTT
#define LUA_USE_MODULES_NET
//#define LUA_USE_MODULES_NODE
//#define LUA_USE_MODULES_OW
#define LUA_USE_MODULES_RTCTIME
#define LUA_USE_MODULES_SNTP
//#define LUA_USE_MODULES_SPI
//#define LUA_USE_MODULES_TLS
#define LUA_USE_MODULES_TMR
//#define LUA_USE_MODULES_UART
#define LUA_USE_MODULES_WIFI
```


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
profile = {}
profile.MODE = <MODE>  -- 0: indoor / 1: outdoor
profile.SSID = "<THE SSID>"
profile.PASSWORD = "<THE PASSWORD>"
profile.BABILONIA_SERVER = "<SERVER IP>"

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
sudo pip install simplejson
sudo pip install pandas
sudo pip3 install flask-mqtt
sudo pip install Pillow
sudo pip install Flask-QRcode
sudo pip install Flask-Assets
sudo pip install jsmin
sudo pip install cssmin

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
    },
    "defaults":{
        "TEMPERATURE_THRESHOLD":"25.00",
        "MASK_CRON_LIGHT_ON":"0 11 * * *",
        "MASK_CRON_LIGHT_OFF":"0 20 * * *",
        "MASK_CRON_CTRL": "*/10 * * * *",
        "SLEEP_TIME_SPRINKLE":"30000000"
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
