#!/bin/bash
#38 09 * * * /babilonia/server/irrigation.sh > /babilonia/server/log/irrigation.log 2>&1 &
NODEID=15566415
TIME=10000000
DATE=`date '+%Y-%m-%d %H:%M:%S'`
CONFIG_FILE='/babilonia/server/app/config.json'
MQTT_HOST=`cat  $CONFIG_FILE | jq -r .mqtt.broker`
PARM="id:$NODEID;sop:$TIME"
mosquitto_pub -h $MQTT_HOST -t "/cfg" -m $PARM
echo "$DATE - $PARM"
