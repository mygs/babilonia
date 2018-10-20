#!/bin/bash
NODEID=15566415
TIME=10000000
DATE=`date '+%Y-%m-%d %H:%M:%S'`
CONFIG_FILE='./app/config.json'
MQTT_HOST=`cat  $CONFIG_FILE | jq -r .mqtt.broker`
PARM="id:$NODEID;sop:$TIME"
mosquitto_pub -h $MQTT_HOST -t "/cfg" -m $PARM
echo "$DATA - $PARM"
