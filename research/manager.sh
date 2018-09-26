#!/bin/bash
NUMBER_OF_SAMPLES=60
CONFIG_FILE='../server/app/config.json'
MQTT_HOST=`cat  $CONFIG_FILE | jq -r .mqtt.broker`
DB_HOST=`cat  $CONFIG_FILE | jq -r .db.host`
DB_USER=`cat  $CONFIG_FILE | jq -r .db.user`
DB_PWD=`cat  $CONFIG_FILE | jq -r .db.password`
DB_TABLE='garden.MOISTURE_TEST_DATA'
MYSQL_INIT_CMD='mysql -h'$DB_HOST' -u'$DB_USER' -p'$DB_PWD' -s -N'
STAT_PREFIX='SELECT count(*) FROM '$DB_TABLE' WHERE'

test(){
  NAME=$1
  STM=$2
  MNS=$3
  MNST=$4
  PARM="stm:"$((1*STM))";mns:"$((1*MNS))";mnst:"$((1*MNST))";cmd:3"
  mosquitto_pub -h $MQTT_HOST -t "/cfg" -m $PARM
  COUNT_READ=0
  while : ; do
      COUNT=`$MYSQL_INIT_CMD -e "$STAT_PREFIX SLEEP_TIME_MOISTURE='$STM' AND MOISTURE_NSAMPLE='$MNS' AND MOISTURE_NSAMPLE_TIME='$MNST'" 2>/dev/null`
      echo 'TEST[#'$NAME' PARM='$PARM'] '$COUNT' of '$NUMBER_OF_SAMPLES
      if [ "$COUNT" -gt "$NUMBER_OF_SAMPLES" ]
      then
        break
      fi
      if [ "$COUNT" -eq 0 ]
      then
        if [ "$COUNT_READ" -gt 5 ]
        then
          mosquitto_pub -h $MQTT_HOST -t "/cfg" -m $PARM
          echo 'WARN: Republished command PARM='$PARM
          COUNT_READ=0
        fi
        COUNT_READ=$(expr $COUNT_READ + 1)
        echo 'WARN: COUNT still ZERO. Forgot it for the '$COUNT_READ' times'
      fi
      sleep 15s
  done
}

test '1s sleep time' 1000000 200 100000
test '2s sleep time' 2000000 200 100000
test '4s sleep time' 4000000 200 100000
test '8s sleep time' 8000000 200 100000
test '100 samples' 5000000 100 200000
test '200 samples' 5000000 200 100000
test '400 samples' 5000000 400 50000
test '800 samples' 5000000 800 25000

echo "FINISHED"
