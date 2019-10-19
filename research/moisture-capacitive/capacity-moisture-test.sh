#!/bin/bash
MESSAGE_ID="water001"
MQTT=192.168.2.1
COLLECT_INTERVAL_SECS=1
TEST_DURATION_SECS=5

N_SAMPLES = TEST_DURATION_SECS/COLLECT_INTERVAL_SECS
#==== Do not change below parameters
TOPIC="/oasis-inbound"
ID="oasis-397988"
MSG="{\"NODE_ID\": \"$ID\", \"MESSAGE_ID\": \"$MESSAGE_ID\",\"STATUS\": [\"CAPACITIVEMOISTURE\"]}"

COUNT_READ=$(expr $COUNT_READ + 1)


echo $MSG

#mosquitto_pub -h $MQTT -t $TOPIC -m $MSG
