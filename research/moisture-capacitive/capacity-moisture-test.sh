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
MQTT_MSG="{\"NODE_ID\": \"$ID\", \"MESSAGE_ID\": \"$MESSAGE_ID\",\"STATUS\": [\"CAPACITIVEMOISTURE\"]}"
##### DATABASE
CONFIG_FILE='../../server/app/config.json'
DB_PWD=`cat  $CONFIG_FILE | jq -r .SECRET_KEY`
SQL='SELECT count(*) FROM farmland.OASIS_DATA WHERE NODE_ID='\'$MQTT_NODE_ID\'
MYSQL_CMD='mysql -h'$SERVER' -ubabilonia -p'$DB_PWD' -s -N -e '\"$SQL\"' 2>/dev/null'
echo 'FULL MYSQL: '$MYSQL_CMD
INITIAL_COUNT=`$MYSQL_CMD`
echo 'Total samples: '$TOTAL_SAMPLES
echo 'Initial count: '$INITIAL_COUNT
LAST_SAMPLE=$((TOTAL_SAMPLES+INITIAL_COUNT))
echo 'Last count: '$LAST_SAMPLE

while : ; do
  #COUNT=`$MYSQL_CMD`
  break
done
echo $MSG

#mosquitto_pub -h $SERVER -t $MQTT_TOPIC -m $MQTT_MSG
