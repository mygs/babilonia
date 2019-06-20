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
espmake ota ESP_ADDR=192.168.2.60
```

### mqtt commands

subscribe all topics
```
mosquitto_sub -h 192.168.2.1 -t "#" -v
```
full message
```
mosquitto_pub -h 192.168.2.1 -t "/oasis-inbound" -m "{\"ID\": \"a12dc89b\",\"CONFIG\": {\"SSID\": \"babilonia\",\"PASSWORD\": \"secret\",\"MQTT_SERVER\": \"192.168.2.1\",\"MQTT_PORT\": 1883,\"MQTT_TOPIC_INBOUND\": \"\/oasis-inbound\",\"MQTT_TOPIC_OUTBOUND\": \"\/oasis-outbound\",\"PERIOD\": 300,\"PIN\":{\"0\": \"IDLE\",\"1\": \"WATER\", \"2\": \"LIGHT\", \"3\": \"SOIL.X\",\"4\": \"DHT\",\"5\": \"SOIL.1\", \"6\": \"SOIL.2\",\"7\": \"SOIL.3\", \"8\": \"SOIL.4\"}},\"COMMAND\": {\"LIGHT\": true,\"FAN\": true,\"WATER\": true,\"REBOOT\": true},\"STATUS\": [\"NODE\", \"SOIL\", \"DHT\", \"LIGHT\", \"FAN\", \"WATER\"]}"
```

config message
```
mosquitto_pub -h 192.168.2.1 -t "/oasis-inbound" -m "{\"ID\": \"a12dc89b\",\"CONFIG\": {\"SSID\": \"babilonia\",\"PASSWORD\": \"secret\",\"MQTT_SERVER\": \"192.168.2.1\",\"MQTT_PORT\": 1883,\"MQTT_TOPIC_INBOUND\": \"\/oasis-inbound\",\"MQTT_TOPIC_OUTBOUND\": \"\/oasis-outbound\",\"PERIOD\": 300,\"PIN\":{\"0\": \"IDLE\",\"1\": \"WATER\", \"2\": \"LIGHT\", \"3\": \"SOIL.X\",\"4\": \"DHT\",\"5\": \"SOIL.1\", \"6\": \"SOIL.2\",\"7\": \"SOIL.3\", \"8\": \"SOIL.4\"}}}"
```
command and status message
```
mosquitto_pub -h 192.168.2.1 -t "/oasis-inbound" -m "{\"ID\": \"a12dc89b\",\"COMMAND\": {\"LIGHT\": true,\"FAN\": true,\"WATER\": true,\"REBOOT\": true},\"STATUS\": [\"NODE\", \"SOIL\", \"DHT\", \"LIGHT\", \"FAN\", \"WATER\"]}"
```

command message
```
mosquitto_pub -h 192.168.2.1 -t "/oasis-inbound" -m "{\"ID\": \"a12dc89b\",\"COMMAND\": {\"LIGHT\": true,\"FAN\": true,\"WATER\": true,\"REBOOT\": true}}"
```

status message
```
mosquitto_pub -h 192.168.2.1 -t "/oasis-inbound" -m "{\"ID\": \"a12dc89b\",\"STATUS\": [\"NODE\", \"SOIL\", \"DHT\", \"LIGHT\", \"FAN\", \"WATER\"]}"
```
