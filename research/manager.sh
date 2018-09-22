#!/bin/bash
STM=1000000 # 1000000, 2000000, 4000000, 8000000
MNS=200      #      100     200    400    800
MNST=100000  #   200000  100000  50000  25000
PARM="stm:"$((1*STM))";mns:"$((1*MNS))";mnst:"$((1*MNST))";cmd:3"
echo $PARM
mosquitto_pub -h 192.168.2.1 -t "/cfg" -m $PARM
sleep 1h
PARM="stm:"$((2*STM))";mns:"$((1*MNS))";mnst:"$((1*MNST))";cmd:3"
echo $PARM
mosquitto_pub -h 192.168.2.1 -t "/cfg" -m $PARM
sleep 1h
PARM="stm:"$((4*STM))";mns:"$((1*MNS))";mnst:"$((1*MNST))";cmd:3"
echo $PARM
mosquitto_pub -h 192.168.2.1 -t "/cfg" -m $PARM
sleep 1h
PARM="stm:"$((8*STM))";mns:"$((1*MNS))";mnst:"$((1*MNST))";cmd:3"
echo $PARM
mosquitto_pub -h 192.168.2.1 -t "/cfg" -m $PARM
sleep 1h
MNS=100      #      100     200    400    800
MNST=200000  #   200000  100000  50000  25000
PARM="stm:"$((5*STM))";mns:"$((1*MNS))";mnst:"$((1*MNST))";cmd:3"
echo $PARM
mosquitto_pub -h 192.168.2.1 -t "/cfg" -m $PARM
sleep 1h
PARM="stm:"$((5*STM))";mns:"$((2*MNS))";mnst:"$((MNST/2))";cmd:3"
echo $PARM
mosquitto_pub -h 192.168.2.1 -t "/cfg" -m $PARM
sleep 1h
PARM="stm:"$((5*STM))";mns:"$((4*MNS))";mnst:"$((MNST/4))";cmd:3"
echo $PARM
mosquitto_pub -h 192.168.2.1 -t "/cfg" -m $PARM
sleep 1h
PARM="stm:"$((5*STM))";mns:"$((8*MNS))";mnst:"$((MNST/8))";cmd:3"
echo $PARM
mosquitto_pub -h 192.168.2.1 -t "/cfg" -m $PARM
sleep 1h
