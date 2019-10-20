#!/bin/bash
MESSAGE_ID="water001"
SERVER=192.168.2.1
COLLECT_INTERVAL_SECS=1
TEST_DURATION_SECS=5



#==== Do not change below parameters

TOTAL_SAMPLES=$((TEST_DURATION_SECS/COLLECT_INTERVAL_SECS))
CONFIG_FILE='../../server/app/config.json'
DB_PWD=`cat  $CONFIG_FILE | jq -r .SECRET_KEY`

MQTT_TOPIC="/oasis-inbound"
MQTT_NODE_ID="oasis-397988"
MQTT_MSG="{\"NODE_ID\": \"$ID\", \"MESSAGE_ID\": \"$MESSAGE_ID\",\"STATUS\": [\"CAPACITIVEMOISTURE\"]}"


MYSQL_INIT_CMD='mysql -h'$SERVER' -ubabilonia -p'$DB_PWD' -s -N'
DB_TABLE='farmland.OASIS_DATA'
QUERY='SELECT count(*) FROM '$DB_TABLE' WHERE NODE_ID=\''$MQTT_NODE_ID


echo 'DB password:'$DB_PWD
echo 'Number of samples: '$TOTAL_SAMPLES
COUNT=`$MYSQL_INIT_CMD -e "$STAT_PREFIX SLEEP_TIME_MOISTURE='$STM' AND MOISTURE_NSAMPLE='$MNS' AND MOISTURE_NSAMPLE_TIME='$MNST'" 2>/dev/null`

while : ; do
  break
done
echo $MSG

#mosquitto_pub -h $SERVER -t $MQTT_TOPIC -m $MQTT_MSG
