#!/bin/bash
MESSAGE_ID="water001"
COLLECT_INTERVAL_SECS=1
TEST_DURATION_SECS=5



#==== Do not touch below here
TOTAL_SAMPLES=$((TEST_DURATION_SECS/COLLECT_INTERVAL_SECS))

SERVER=192.168.1.70
if [ `hostname` = "babilonia" ]; then
  SERVER=192.168.2.1
fi
##### MQTT
MQTT_TOPIC="/oasis-inbound"
MQTT_NODE_ID="oasis-397988"
##### DATABASE
CONFIG_FILE='../../server/app/config.json'
DB_PWD=`cat  $CONFIG_FILE | jq -r .SECRET_KEY`

echo '########################################'
START=`date +%s`
OFFSET_COUNT=`mysql -h$SERVER -ubabilonia -p$DB_PWD -s -N -e "SELECT count(*) FROM farmland.OASIS_DATA WHERE NODE_ID='$MQTT_NODE_ID'" 2>/dev/null`
echo 'Total samples: '$TOTAL_SAMPLES
LAST_SAMPLE=$((TOTAL_SAMPLES+OFFSET_COUNT))
COUNT=$OFFSET_COUNT
while [ "$COUNT" -le "$LAST_SAMPLE" ] ; do
  mosquitto_pub -h $SERVER -t $MQTT_TOPIC -m "{\"NODE_ID\": \"$MQTT_NODE_ID\", \"MESSAGE_ID\": \"$MESSAGE_ID\",\"STATUS\": [\"CAPACITIVEMOISTURE\"]}"
  sleep $COLLECT_INTERVAL_SECS
  COUNT=`mysql -h$SERVER -ubabilonia -p$DB_PWD -s -N -e "SELECT count(*) FROM farmland.OASIS_DATA WHERE NODE_ID='$MQTT_NODE_ID'" 2>/dev/null`
  echo $((COUNT-OFFSET_COUNT))' of '$TOTAL_SAMPLES
done
END=`date +%s`
echo "Execution time was `expr $end - $start` seconds."
echo '########################################'
