Install the following tools
## TOOLS
In $BABILONIA_LIBS
```bash
git clone --recursive https://github.com/pfalcon/esp-open-sdk.git
make
git clone https://github.com/plerup/makeEspArduino.git
git checkout tags/4.16.1
git clone https://github.com/knolleary/pubsubclient.git
git checkout tags/v2.7
git clone https://github.com/esp8266/Arduino.git esp8266
git checkout tags/2.5.0
cd esp8266/tools
python get.py
git clone https://github.com/bblanchon/ArduinoJson.git
git checkout tags/v6.9.1
```


Set the following environment variables
## ENVIRONMENT VARIABLE
/etc/profile.d/00-babilonia.sh
```bash
export BABILONIA_LIBS=/github
PATH=$PATH:$BABILONIA_LIBS/esp-open-sdk/xtensa-lx106-elf/bin
alias xgcc="xtensa-lx106-elf-gcc"
alias espmake="make -f $BABILONIA_LIBS/makeEspArduino/makeEspArduino.mk"
export BABILONIA_HOME=/github/babilonia
```


## Over The Air
First update, must be through USB
```bash
espmake flash
```
Then, OTA
```bash
espmake ota ESP_ADDR=HOSTNAME.local
```
