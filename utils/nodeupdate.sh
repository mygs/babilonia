#!/bin/bash
mkdir /tmp/_____BAB____
echo ""
echo "############################"
echo "# NODE AUTO UPDATE MANAGER #"
echo "############################"
echo ""
NODE_IS_PLUGGED=$(lsusb | grep -e "1a86:7523")
if [[ ! -z $NODE_IS_PLUGGED ]]; then
   mkdir /tmp/_____BABX_____

#  echo "Updating source code..."
  cd $BABILONIA_HOME
#  git pull
  echo "Building binaries..."
  cd $BABILONIA_HOME/node
  ./luac.cross -o config.lc config.lua
  ./luac.cross -o apps.lc apps.lua
  echo "Cleaning old binaries from NODE..."
  nodemcu-uploader file remove init.lua apps.lc config.lc nconfig.lua
  echo "Restarting NODE..."
  nodemcu-uploader node restart
  sleep 5
  echo "Uploading..."
  nodemcu-uploader upload config.lc apps.lc init.lua
  exit 0
else
  echo "NODE is not plugged"
  exit 1
fi
