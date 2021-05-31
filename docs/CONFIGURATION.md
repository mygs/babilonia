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

### USB rule
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



# TROUBLESHOOTING
Node terminal through USB connection
```bash
nodemcu-uploader terminal
```

Exception decoder
```bash
git clone https://github.com/janLo/EspArduinoExceptionDecoder.git
./decoder.py -e /tmp/mkESP/Oasis_nodemcuv2/Oasis.elf myStackTrace.txt
```

Restart server service
```bash
sudo service nabucodonosor restart
```

Subscribe all MQTT topics
```bash
mosquitto_sub -h 192.168.2.1 -t "#" -v
```


Node configuration full message
```bash
mosquitto_pub -h 192.168.2.1 -t "/oasis-inbound" -m "{\"MESSAGE_ID\": \"a12dc89b\",\"CONFIG\": {\"SSID\": \"babilonia\",\"PASSWORD\": \"secret\",\"MQTT_SERVER\": \"192.168.2.1\",\"MQTT_PORT\": 1883,\"MQTT_TOPIC_INBOUND\": \"\/oasis-inbound\",\"MQTT_TOPIC_OUTBOUND\": \"\/oasis-outbound\",\"PERIOD\": 300,\"PIN\":{\"0\": \"IDLE\",\"1\": \"WATER\", \"2\": \"LIGHT\", \"3\": \"SOIL.X\",\"4\": \"DHT\",\"5\": \"SOIL.1\", \"6\": \"SOIL.2\",\"7\": \"SOIL.3\", \"8\": \"SOIL.4\"}},\"COMMAND\": {\"LIGHT\": true,\"FAN\": true,\"WATER\": true,\"REBOOT\": true},\"STATUS\": [\"NODE\", \"SOIL\", \"DHT\", \"LIGHT\", \"FAN\", \"WATER\"]}"
```

Node port configuration message
```bash
mosquitto_pub -h 192.168.2.1 -t "/oasis-inbound" -m "{\"NODE_ID\": \"oasis-312193\",\"MESSAGE_ID\": \"a12dc89b\",\"CONFIG\": {\"PIN\":{\"0\": \"WATER\",\"1\": \"IDLE\", \"2\": \"LIGHT\", \"3\": \"SOIL.X\",\"4\": \"DHT\",\"5\": \"SOIL.1\", \"6\": \"SOIL.2\",\"7\": \"SOIL.3\", \"8\": \"SOIL.4\"}}}"
```

Node frequencies configuration message
```bash
mosquitto_pub -h 192.168.2.1 -t "/oasis-inbound" -m "{\"NODE_ID\": \"oasis-312193\",\"MESSAGE_ID\": \"a12dc89b\",\"CONFIG\": {\"HEARTBEAT_PERIOD\": 31}}"

mosquitto_pub -h 192.168.2.1 -t "/oasis-inbound" -m "{\"NODE_ID\": \"ALL\",\"MESSAGE_ID\": \"a12dc89b\",\"CONFIG\": {\"HEARTBEAT_PERIOD\": 3000, \"SENSOR_COLLECT_DATA_PERIOD\": 30000}}"

#ZIBA
mosquitto_pub -h 192.168.2.1 -t "/oasis-inbound" -m "{\"NODE_ID\": \"oasis-312209\",\"MESSAGE_ID\": \"fix_conn_issue\",\"CONFIG\": {\"MQTT_SERVER\": \"192.168.0.90\", \"SSID\": \"babilonia-ext\"}}"
```

Node command and status message
```bash
mosquitto_pub -h 192.168.2.1 -t "/oasis-inbound" -m "{\"MESSAGE_ID\": \"a12dc89b\",\"COMMAND\": {\"LIGHT\": true,\"FAN\": true,\"WATER\": true,\"REBOOT\": true},\"STATUS\": [\"NODE\", \"SOIL\", \"DHT\", \"LIGHT\", \"FAN\", \"WATER\"]}"
```

Node reset command
```bash
mosquitto_pub -h 192.168.2.1 -t "/oasis-inbound" -m "{\"NODE_ID\": \"ALL\",\"MESSAGE_ID\": \"fix_conn_issue\",\"COMMAND\": {\"RESET\": true}}"
```

Node status message
```bash
mosquitto_pub -h 192.168.2.1 -t "/oasis-inbound" -m "{\"NODE_ID\": \"oasis-312193\", \"MESSAGE_ID\": \"a12dc89b\",\"STATUS\": [\"NODE\", \"SOIL\", \"DHT\", \"LIGHT\", \"FAN\", \"WATER\"]}"
```

Node status message capacitive
```bash
mosquitto_pub -h 192.168.2.1 -t "/oasis-inbound" -m "{\"NODE_ID\": \"oasis-397988\", \"MESSAGE_ID\": \"a12dc89b\",\"STATUS\": [\"CAPACITIVEMOISTURE\"]}"
```

Node Light command
```bash
mosquitto_pub -h 192.168.2.1 -t "/oasis-inbound" -m "{\"NODE_ID\": \"oasis-311de9\", \"MESSAGE_ID\": \"test\",\"COMMAND\": {\"LIGHT\": true}}"
```

Node Log command
```bash
mosquitto_pub -h 192.168.0.90 -t "/oasis-inbound" -m "{\"NODE_ID\": \"oasis-ed8653\", \"MESSAGE_ID\": \"log_test\",\"LOG\": true}"
```