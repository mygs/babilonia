#!/bin/bash
echo ""
echo "#############################"
echo "# NODE UPDATE CONFIGURATION #"
echo "#############################"
echo ""

MKSPIFFS="$BABILONIA_LIBS/esp8266/tools/mkspiffs/mkspiffs"
ESPTOOL="$BABILONIA_LIBS/esp8266/tools/esptool/esptool"

case "$OSTYPE" in
  darwin*)
    UPLOAD_PORT="/dev/tty.wchusbserial1420"
    ;;
  linux*)
    UPLOAD_PORT="/dev/ttyUSB0"
    ;;
  *)
    echo "unknown: $OSTYPE"
    exit 1
    ;;
esac

$MKSPIFFS -c $BABILONIA_HOME/node/ino/config/ -p 256 -b 8192 -s 1028096 /tmp/config.spiffs
$ESPTOOL -v -cd nodemcu -cb 115200 -cp $UPLOAD_PORT -ca 0x300000 -cf /tmp/config.spiffs
