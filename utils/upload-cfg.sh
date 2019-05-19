#!/bin/bash
echo ""
echo "#############################"
echo "# NODE UPDATE CONFIGURATION #"
echo "#############################"
echo ""

MKSPIFFS="$BABILONIA_LIBS/esp8266/tools/mkspiffs/mkspiffs"
ESPTOOL="$BABILONIA_LIBS/esp8266/tools/esptool/esptool"

$MKSPIFFS -c $BABILONIA_HOME/node/ino/config/ -p 256 -b 8192 -s 1028096 /tmp/configuration.spiffs
$ESPTOOL -v -cd nodemcu -cb 115200 -cp /dev/ttyUSB0 -ca 0x300000 -cf /tmp/configuration.spiffs
