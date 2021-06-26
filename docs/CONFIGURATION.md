# SERVER CONFIGURATION

### SERVER ENVIRONMENT VARIABLE
Set the following environment variables

/etc/profile.d/00-babilonia.sh
```bash
export BABILONIA_LIBS=/github
export BABILONIA_HOME=/github/babilonia
PATH=$PATH:$BABILONIA_LIBS/esptool
alias espmake="make -f $BABILONIA_LIBS/makeEspArduino/makeEspArduino.mk"
```

### SERVER APPLICATION AS DAEMON
```bash
dos2unix nabucodonosor.sh
sudo chmod 755 nabucodonosor.py
sudo chmod 755 nabucodonosor.sh
sudo cp nabucodonosor.sh /etc/init.d
sudo update-rc.d nabucodonosor.sh defaults
sudo /etc/init.d/nabucodonosor.sh start
sudo /etc/init.d/nabucodonosor.sh status
```

### COPYING SERVER IMAGE
1) sudo dd bs=4M if=/dev/sd{c,d} of=/tmp/babilonia.img
2) (ubuntu host) Make Startup Disk
3) gzip babilonia.img
4) connect via ssh
4.1) sudo service nabucodonosor stop
4.2) sudo service noip2 stop
4.3) sudo rm /usr/local/etc/no-ip2.conf
4.4) sudo noip2 -C


### MIDDLWARES & TOOLS
```bash
sudo apt install dos2unix mysql-server mysql-client mosquitto python3-mysqldb
```

### DEVELOPMENT LIBRARIES
Install the following tools in $BABILONIA_LIBS
```bash
git clone https://github.com/plerup/makeEspArduino.git
git checkout tags/4.17.0
git clone https://github.com/knolleary/pubsubclient.git
git checkout tags/v2.7
git clone https://github.com/esp8266/Arduino.git esp8266
git checkout tags/2.5.0
cd esp8266/tools
python get.py
git clone https://github.com/bblanchon/ArduinoJson.git
git checkout tags/v6.9.1
git clone https://github.com/espressif/esptool.git
git checkout tags/v2.6
git clone https://github.com/adafruit/DHT-sensor-library.git
git checkout tags/1.3.7
```
### Code formatting

[Black, the Uncompromising Code Formatter](https://github.com/psf/black)
```bash
pip install git+git://github.com/psf/black
```


### SERVER APPLICATION DEPENDENCIES
Update requirements.txt
```bash
pipreqs --force .
```
Simple do:
```bash
pip3 install -r requirements.txt
```
OR
```bash
sudo pip3 install paho-mqtt sqlalchemy flask-sqlalchemy flask-mysql flask-socketio simplejson pandas flask-mqtt Pillow Flask-QRcode Flask-Assets jsmin cssmin
pathlib python-git gitpython
```


### GPIO CONFIGURATION
```
sudo pip3 install RPi.GPIO
sudo groupadd gpio
sudo usermod -a -G gpio msaito
sudo chown root.gpio /dev/gpiomem
sudo chmod g+rw /dev/gpiomem
$ cat /etc/udev/rules.d/71-gpio.rules
SUBSYSTEM=="bcm2835-gpiomem", KERNEL=="gpiomem", GROUP="gpio", MODE="0660"
SUBSYSTEM=="gpio", KERNEL=="gpiochip*", ACTION=="add", PROGRAM="/bin/sh -c 'chown root:gpio /sys/class/gpio/export /sys/class/gpio/unexport ; chmod 220 /sys/class/gpio/export /sys/class/gpio/unexport'"
SUBSYSTEM=="gpio", KERNEL=="gpio*", ACTION=="add", PROGRAM="/bin/sh -c 'chown root:gpio /sys%p/active_low /sys%p/direction /sys%p/edge /sys%p/value ; chmod 660 /sys%p/active_low /sys%p/direction /sys%p/edge /sys%p/value

```

### USB rule (deprecated)
/etc/udev/rules.d/babilonia.rules

```bash
SUBSYSTEM=="usb", ACTION=="add", ENV{DEVTYPE}=="usb_device", ENV{ID_VENDOR}=="1a86", RUN+="/babilonia/utils/nodeupdate.sh"
```

### GEODATA
https://darksky.net/dev/docs
https://api.darksky.net/forecast/[key]/[latitude],[longitude]
https://api.darksky.net/forecast/4b7af3b7a119ca4b0ea27681f8472504/-23.535521,-46.763048?units=si


### GUNICORN DAEMON
```bash
sudo pip3 install gunicorn
```
https://bartsimons.me/gunicorn-as-a-systemd-service/

```bash
gunicorn -b 0.0.0.0:8181 --chdir /github/babilonia/server/app nabucodonosor:app --daemon
```
```bash
sudo pkill gunicorn
```
copy nabucodonosor.service to /etc/systemd/system/

```bash
sudo chmod 755 /etc/systemd/system/nabucodonosor.service
sudo systemctl daemon-reload
# Start your service
sudo systemctl start nabucodonosor.service
# Obtain your services' status
sudo systemctl status nabucodonosor.service
# Stop your service
sudo systemctl stop nabucodonosor.service

# Restart your service
sudo systemctl restart nabucodonosor.service
```


### Backup/Clone Server Image
```bash
sudo dd bs=4M if=/dev/sdd of=/tmp/babilonia.img
gzip babilonia.img
```

### Create new Server based on clone image
1) Extracted babilonia.img.gz
2) Using gnome-disk-utility > "Restore Disk Image ..." > Select babilonia.img > "Start Restoring"
3) mount micro usb and change:
3.1) SSID:
3.1.1) <mount_point>/etc/netplan/28-babilonia-wifi.yaml
3.1.2) <mount_point>/github/babilonia/node/ino/InitialConfiguration.h
3.2) HOSTNAME:
3.2.1) <mount_point>/etc/hosts
3.2.2) <mount_point>/etc/hostname
3.2.3) <mount_point>/etc/cloud/cloud.cfg
3.3) WIRE NETWORK:
3.3.1) Update <mount_point>/etc/netplan/18-babilonia-wire.yaml
3.4) MOTD:
3.3.1) Update <mount_point>/etc/update-motd.d/50-babilonia

4) After boot using Raspberry Pi:
4.1) Clear all database data;
4.2) Update no-ip configuration
4.3) Uninstall Wireguard


### MANAGE SERVICES
####  MYSQL
status/start/stop
```bash
service mysql status
sudo service mysql stop
sudo service mysql start
```
auto/manual startup
```bash
sudo update-rc.d mysql remove
sudo update-rc.d mysql defaults
sudo systemctl disable mysql
```

####  MOSQUITTO
status/start/stop
```bash
service mosquitto status
sudo service mosquitto stop
sudo service mosquitto start
```
auto/manual startup
```bash
sudo update-rc.d mosquitto remove
sudo update-rc.d mosquitto defaults
sudo systemctl disable mosquitto

```

# NODE CONFIGURATION

### Update Over The Air
First update, must be through USB
```bash
espmake flash
```
Then, OTA
```bash
espmake ota ESP_ADDR=192.168.2.102
```
### InitialConfiguration
```c
#ifndef __INITIALCONFIGURATION_H
#define __INITIALCONFIGURATION_H

#include "OasisConstants.h"

namespace InitialConfiguration {
 const char* SSID     = "<WIFI_SSID>>";
 const char* PASSWORD = "<WIFI_PASSWD>>";
 const char* MQTT_SERVER = "<<MQTT_SERVER>>";
 const int   MQTT_PORT = 1883;
 const char* MQTT_TOPIC_HEARTBEAT = "/oasis-heartbeat";
 const char* MQTT_TOPIC_INBOUND = "/oasis-inbound";
 const char* MQTT_TOPIC_OUTBOUND = "/oasis-outbound";
 const int   SERIAL_BAUDRATE = 115200;
 const int   OTA_PORT = 8266;
 //milliseconds
 const int   HEARTBEAT_PERIOD = 15000;
 const int   SENSOR_COLLECT_DATA_PERIOD = 30000;
 const int   RETRY_WIFI_CONN_DELAY = 5000;

 const char* PINA     = NODE::CAPACITIVEMOISTURE;
 const char* PIN0     = NODE::IDLE;
 const char* PIN1     = NODE::WATER;  //fixed in shield
 const char* PIN2     = NODE::IDLE;
 //const char* PIN2     = NODE::LIGHT;
 const char* PIN3     = NODE::IDLE;
 const char* PIN4     = NODE::DHT;   //fixed in shield
 const char* PIN5     = NODE::CHANNEL_SELECT_A;
 const char* PIN6     = NODE::CHANNEL_SELECT_B;
 const char* PIN7     = NODE::CHANNEL_SELECT_C;
 const char* PIN8     = NODE::IDLE;
}

#endif // ifndef __INITIALCONFIGURATION_H

```
