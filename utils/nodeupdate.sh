#!/bin/bash
echo ""
echo "############################"
echo "# NODE AUTO UPDATE MANAGER #"
echo "############################"
echo ""
NODE_IS_PLUGGED=$(lsusb | grep -e "1a86:7523")
if [[ ! -z $NODE_IS_PLUGGED ]]; then
  echo "Building binaries..."
  cd /babilonia/node
  ./luac.cross -o config.lc config.lua
  ./luac.cross -o apps.lc apps.lua
  ./luac.cross -o moistureTest.lc moistureTest.lua
  echo "Cleaning old binaries and confs from NODE..."
  nodemcu-uploader file remove profile.lua init.lua apps.lc moistureTest.lc config.lc nconfig.lua remote.reboot fan.on light.on
  echo "Restarting NODE..."
  nodemcu-uploader node restart
  sleep 5
  echo "Uploading..."
  nodemcu-uploader upload profile.lua config.lc apps.lc moistureTest.lc init.lua
  exit 0
else
  echo "NODE is not plugged"
  exit 1
fi
