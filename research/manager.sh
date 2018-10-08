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
  PARM="id:3767310;stm:"$((1*STM))";mns:"$((1*MNS))";mnst:"$((1*MNST))";cmd:3"
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

#test '[1s200x0.100s] 1s sleep time' 1000000 200 100000
#test '[2s200x0.100s] 2s sleep time' 2000000 200 100000
#test '[4s200x0.100s] 4s sleep time' 4000000 200 100000
#test '[8s200x0.100s] 8s sleep time' 8000000 200 100000
test '[5s050x]' 5000000 50 400000
test '[5s100x]' 5000000 100 200000
test '[5s150x]' 5000000 150 133333
test '[5s200x]' 5000000 200 100000
test '[5s250x]' 5000000 250 80000
test '[5s300x]' 5000000 300 66667
test '[5s350x]' 5000000 350 57143
test '[5s400x]' 5000000 400 50000
test '[5s450x]' 5000000 450 44444
test '[5s500x]' 5000000 500 40000
test '[5s550x]' 5000000 550 36364
test '[5s600x]' 5000000 600 33333
test '[5s650x]' 5000000 650 30769
test '[5s700x]' 5000000 700 28571
test '[5s750x]' 5000000 750 26667
test '[5s800x]' 5000000 800 25000
test '[5s850x]' 5000000 850 23529
test '[5s900x]' 5000000 900 22222
test '[5s950x]' 5000000 950 21053



echo "FINISHED"
