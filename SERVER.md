## GEOCODE

#### FIND LAT and LNG
http://www.datasciencetoolkit.org/
```
[{"types":["locality","political"],"address_components":[{"types":["locality","political"],"long_name":"Osasco, BR","short_name":"Osasco"},{"types":["country","political"],"long_name":"Brazil","short_name":"BR"}],"geometry":{"location":{"lng":-46.79167,"lat":-23.5325},"location_type":"APPROXIMATE","viewport":{"southwest":{"lng":-46.8106842041,"lat":-23.5616264343},"northeast":{"lng":-46.7097053528,"lat":-23.4430885315}}}}]
```
latitude = /results/geometry/location/lat
longitude = /results/geometry/location/lng

ref: https://github.com/M0nica/flask_weather/blob/master/app.py


#### GEODATA
https://darksky.net/dev/docs
```
https://api.darksky.net/forecast/[key]/[latitude],[longitude]
```
https://api.darksky.net/forecast/4b7af3b7a119ca4b0ea27681f8472504/-23.535521,-46.763048?units=si
https://api.forecast.io/forecast/4b7af3b7a119ca4b0ea27681f8472504/-23.535521,-46.763048?units=si

## ENVIRONMENT VARIABLE
Set the following environment variables

/etc/profile.d/00-babilonia.sh
```bash
export BABILONIA_LIBS=/github
export BABILONIA_HOME=/github/babilonia
PATH=$PATH:$BABILONIA_LIBS/esptool:$BABILONIA_LIBS/esp-open-sdk/xtensa-lx106-elf/bin
alias xgcc="xtensa-lx106-elf-gcc"
alias espmake="make -f $BABILONIA_LIBS/makeEspArduino/makeEspArduino.mk"
```

### python imports
Update requirements.txt
```
pipreqs --force .
```
Simple do:
```
pip3 install -r requirements.txt
```
OR
```
sudo pip3 install paho-mqtt sqlalchemy flask-sqlalchemy flask-mysql flask-socketio simplejson pandas flask-mqtt Pillow Flask-QRcode Flask-Assets jsmin cssmin
pathlib python-git gitpython
```

### middlwares & tools
```
sudo apt-get install mysql-server && sudo apt-get install mysql-client
sudo apt-get install dos2unix
sudo apt-get install python3-mysqldb
```



## TOOLS
Install the following tools in $BABILONIA_LIBS
```bash
git clone --recursive https://github.com/pfalcon/esp-open-sdk.git
make
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

## DECODE EXCEPTION
```bash
git clone https://github.com/janLo/EspArduinoExceptionDecoder.git
./decoder.py -e /tmp/mkESP/Oasis_nodemcuv2/Oasis.elf myStackTrace.txt
```
## Over The Air
First update, must be through USB
```bash
espmake flash
```
Then, OTA
```bash
espmake ota ESP_ADDR=192.168.2.102
```

### mqtt commands

subscribe all topics
```
mosquitto_sub -h 192.168.2.1 -t "#" -v
```
full message
```
mosquitto_pub -h 192.168.2.1 -t "/oasis-inbound" -m "{\"MESSAGE_ID\": \"a12dc89b\",\"CONFIG\": {\"SSID\": \"babilonia\",\"PASSWORD\": \"secret\",\"MQTT_SERVER\": \"192.168.2.1\",\"MQTT_PORT\": 1883,\"MQTT_TOPIC_INBOUND\": \"\/oasis-inbound\",\"MQTT_TOPIC_OUTBOUND\": \"\/oasis-outbound\",\"PERIOD\": 300,\"PIN\":{\"0\": \"IDLE\",\"1\": \"WATER\", \"2\": \"LIGHT\", \"3\": \"SOIL.X\",\"4\": \"DHT\",\"5\": \"SOIL.1\", \"6\": \"SOIL.2\",\"7\": \"SOIL.3\", \"8\": \"SOIL.4\"}},\"COMMAND\": {\"LIGHT\": true,\"FAN\": true,\"WATER\": true,\"REBOOT\": true},\"STATUS\": [\"NODE\", \"SOIL\", \"DHT\", \"LIGHT\", \"FAN\", \"WATER\"]}"
```

config message
```
mosquitto_pub -h 192.168.2.1 -t "/oasis-inbound" -m "{\"NODE_ID\": \"oasis-312193\",\"MESSAGE_ID\": \"a12dc89b\",\"CONFIG\": {\"PIN\":{\"0\": \"WATER\",\"1\": \"IDLE\", \"2\": \"LIGHT\", \"3\": \"SOIL.X\",\"4\": \"DHT\",\"5\": \"SOIL.1\", \"6\": \"SOIL.2\",\"7\": \"SOIL.3\", \"8\": \"SOIL.4\"}}}"
```

HEARTBEAT_PERIOD config message
```
mosquitto_pub -h 192.168.2.1 -t "/oasis-inbound" -m "{\"NODE_ID\": \"oasis-312193\",\"MESSAGE_ID\": \"a12dc89b\",\"CONFIG\": {\"HEARTBEAT_PERIOD\": 31}}"

mosquitto_pub -h 192.168.2.1 -t "/oasis-inbound" -m "{\"NODE_ID\": \"ALL\",\"MESSAGE_ID\": \"a12dc89b\",\"CONFIG\": {\"HEARTBEAT_PERIOD\": 3000, \"SENSOR_COLLECT_DATA_PERIOD\": 30000}}"
```

command and status message
```
mosquitto_pub -h 192.168.2.1 -t "/oasis-inbound" -m "{\"MESSAGE_ID\": \"a12dc89b\",\"COMMAND\": {\"LIGHT\": true,\"FAN\": true,\"WATER\": true,\"REBOOT\": true},\"STATUS\": [\"NODE\", \"SOIL\", \"DHT\", \"LIGHT\", \"FAN\", \"WATER\"]}"
```

command RESET
```
mosquitto_pub -h 192.168.2.1 -t "/oasis-inbound" -m "{\"NODE_ID\": \"oasis-39732c\",\"MESSAGE_ID\": \"a12dc89b\",\"COMMAND\": {\"RESET\": true}}"
```

command message
```
mosquitto_pub -h 192.168.2.1 -t "/oasis-inbound" -m "{\"NODE_ID\": \"oasis-312193\",\"MESSAGE_ID\": \"a12dc89b\",\"COMMAND\": {\"LIGHT\": true,\"FAN\": true,\"WATER\": true,\"REBOOT\": false}}"

mosquitto_pub -h 192.168.2.1 -t "/oasis-inbound" -m "{\"NODE_ID\": \"oasis-312193\",\"MESSAGE_ID\": \"a12dc89b\",\"COMMAND\": {\"LIGHT\": true}}"
```

status message
```
mosquitto_pub -h 192.168.2.1 -t "/oasis-inbound" -m "{\"NODE_ID\": \"oasis-312193\", \"MESSAGE_ID\": \"a12dc89b\",\"STATUS\": [\"NODE\", \"SOIL\", \"DHT\", \"LIGHT\", \"FAN\", \"WATER\"]}"
```

status message node
```
mosquitto_pub -h 192.168.2.1 -t "/oasis-inbound" -m "{\"NODE_ID\": \"oasis-312193\", \"MESSAGE_ID\": \"a12dc89b\",\"STATUS\": [\"NODE\"]}"
```
status message capacitive
```
mosquitto_pub -h 192.168.2.1 -t "/oasis-inbound" -m "{\"NODE_ID\": \"oasis-397988\", \"MESSAGE_ID\": \"a12dc89b\",\"STATUS\": [\"CAPACITIVEMOISTURE\"]}"
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

sudo service nabucodonosor stop
```

Config
```
mosquitto_pub -h 192.168.2.1 -t "/oasis-inbound" -m "{\"NODE_ID\": \"oasis-397988\",\"MESSAGE_ID\": \"test\",\"CONFIG\": {\"HEARTBEAT_PERIOD\": 15001, \"SENSOR_COLLECT_DATA_PERIOD\": 30001, \"PIN\":{\"A\": \"CAPACITIVEMOISTURE\", \"0\": \"IDLE\",\"1\": \"WATER\", \"2\": \"IDLE\", \"3\": \"IDLE\",\"4\": \"IDLE\",\"5\": \"SW.A\", \"6\": \"SW.B\",\"7\": \"SW.C\", \"8\": \"IDLE\"}}}"
```
command WATER
```
mosquitto_pub -h 192.168.2.1 -t "/oasis-inbound" -m "{\"NODE_ID\": \"oasis-39732c\",\"MESSAGE_ID\": \"a12dc89b\",\"COMMAND\": {\"WATER\": true}}"
```




### SSL
```
certbot certonly --manual -d amitis.ddns.net
```
