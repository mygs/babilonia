# TROUBLESHOOTING
## Node terminal through USB connection
```bash
nodemcu-uploader terminal
```

## Exception decoder
```bash
git clone https://github.com/janLo/EspArduinoExceptionDecoder.git
./decoder.py -e /tmp/mkESP/Oasis_nodemcuv2/Oasis.elf myStackTrace.txt
```

## Restart server service
```bash
sudo service nabucodonosor restart
```

## Subscribe all MQTT topics
```bash
mosquitto_sub -h 10.0.0.30 -t "#" -v
```


## Node configuration full message
```bash
mosquitto_pub -h 192.168.2.1 -t "/oasis-inbound" -m "{\"MESSAGE_ID\": \"a12dc89b\",\"CONFIG\": {\"SSID\": \"babilonia\",\"PASSWORD\": \"secret\",\"MQTT_SERVER\": \"192.168.2.1\",\"MQTT_PORT\": 1883,\"MQTT_TOPIC_INBOUND\": \"\/oasis-inbound\",\"MQTT_TOPIC_OUTBOUND\": \"\/oasis-outbound\",\"PERIOD\": 300,\"PIN\":{\"0\": \"IDLE\",\"1\": \"WATER\", \"2\": \"LIGHT\", \"3\": \"SOIL.X\",\"4\": \"DHT\",\"5\": \"SOIL.1\", \"6\": \"SOIL.2\",\"7\": \"SOIL.3\", \"8\": \"SOIL.4\"}},\"COMMAND\": {\"LIGHT\": true,\"FAN\": true,\"WATER\": true,\"REBOOT\": true},\"STATUS\": [\"NODE\", \"SOIL\", \"DHT\", \"LIGHT\", \"FAN\", \"WATER\"]}"
```

## Node port configuration message
```bash
mosquitto_pub -h 192.168.2.1 -t "/oasis-inbound" -m "{\"NODE_ID\": \"oasis-312193\",\"MESSAGE_ID\": \"a12dc89b\",\"CONFIG\": {\"PIN\":{\"0\": \"WATER\",\"1\": \"IDLE\", \"2\": \"LIGHT\", \"3\": \"SOIL.X\",\"4\": \"DHT\",\"5\": \"SOIL.1\", \"6\": \"SOIL.2\",\"7\": \"SOIL.3\", \"8\": \"SOIL.4\"}}}"
```

## Node frequencies configuration message
```bash
mosquitto_pub -h 192.168.2.1 -t "/oasis-inbound" -m "{\"NODE_ID\": \"oasis-312193\",\"MESSAGE_ID\": \"a12dc89b\",\"CONFIG\": {\"HEARTBEAT_PERIOD\": 31}}"

mosquitto_pub -h 192.168.2.1 -t "/oasis-inbound" -m "{\"NODE_ID\": \"ALL\",\"MESSAGE_ID\": \"a12dc89b\",\"CONFIG\": {\"HEARTBEAT_PERIOD\": 3000, \"SENSOR_COLLECT_DATA_PERIOD\": 30000}}"

#ZIBA
mosquitto_pub -h 192.168.2.1 -t "/oasis-inbound" -m "{\"NODE_ID\": \"oasis-312209\",\"MESSAGE_ID\": \"fix_conn_issue\",\"CONFIG\": {\"MQTT_SERVER\": \"192.168.0.90\", \"SSID\": \"babilonia-ext\"}}"
```

## Node command and status message
```bash
mosquitto_pub -h 192.168.2.1 -t "/oasis-inbound" -m "{\"MESSAGE_ID\": \"a12dc89b\",\"COMMAND\": {\"LIGHT\": true,\"FAN\": true,\"WATER\": true,\"REBOOT\": true},\"STATUS\": [\"NODE\", \"SOIL\", \"DHT\", \"LIGHT\", \"FAN\", \"WATER\"]}"
```

## Node reset command
```bash
mosquitto_pub -h 192.168.2.1 -t "/oasis-inbound" -m "{\"NODE_ID\": \"ALL\",\"MESSAGE_ID\": \"fix_conn_issue\",\"COMMAND\": {\"RESET\": true}}"
```

## Node status message
```bash
mosquitto_pub -h 192.168.2.1 -t "/oasis-inbound" -m "{\"NODE_ID\": \"oasis-312193\", \"MESSAGE_ID\": \"a12dc89b\",\"STATUS\": [\"NODE\", \"SOIL\", \"DHT\", \"LIGHT\", \"FAN\", \"WATER\"]}"
```

## Node status message capacitive
```bash
mosquitto_pub -h 192.168.2.1 -t "/oasis-inbound" -m "{\"NODE_ID\": \"oasis-397988\", \"MESSAGE_ID\": \"a12dc89b\",\"STATUS\": [\"CAPACITIVEMOISTURE\"]}"
```

## Node Light command
```bash
mosquitto_pub -h 192.168.2.1 -t "/oasis-inbound" -m "{\"NODE_ID\": \"oasis-311de9\", \"MESSAGE_ID\": \"test\",\"COMMAND\": {\"LIGHT\": true}}"
```

## Node Switch A command
```bash
mosquitto_pub -h 10.0.0.30 -t "/support-inbound" -m "{\"NODE_ID\": \"oasis-31e1e7\", \"MESSAGE_ID\": \"test\",\"COMMAND\": {\"SWITCH_A\": true}}"
```

## Node Log command
```bash
mosquitto_pub -h 10.0.0.30 -t "/oasis-inbound" -m "{\"NODE_ID\": \"oasis-311de9\", \"MESSAGE_ID\": \"log_test\",\"LOG\": true}"
```
