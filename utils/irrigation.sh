#!/bin/bash
#sudo crontab -e
#10 17 * * * /babilonia/server/irrigation.sh > /babilonia/server/log/irrigation.log 2>&1 &
NODEID=15566415 #OASIS 1X - outdoor
TIME=300000000 # 5min
DATE=`date '+%Y-%m-%d %H:%M:%S'`
CONFIG_FILE='/babilonia/server/app/config.json'
MQTT_HOST=`cat $CONFIG_FILE | jq -r .mqtt.broker`
PARM="id:$NODEID;sop:$TIME"
mosquitto_pub -h $MQTT_HOST -t "/cfg" -m $PARM
echo "$DATE - $PARM"
