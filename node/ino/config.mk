SKETCH = Oasis.ino

ESP_ROOT = $(BABILONIA_LIBS)/esp8266
ESP_LIBS =	$(ESP_ROOT)/libraries

CUSTOM_LIBS =	$(BABILONIA_LIBS)/pubsubclient \
							$(BABILONIA_LIBS)/ArduinoJson/src

GIT_VERSION := $(shell git describe --tags --always)

BUILD_EXTRA_FLAGS = -DMQTT_MAX_PACKET_SIZE=1024 \
									 -DFIRMWARE_VERSION=\"$(GIT_VERSION)\"
#								-Og -ggdb -DDEBUG_ESP_PORT=Serial

#Board type
BOARD = nodemcuv2

FLASH_DEF = 4M1M

ESP_PORT = 8266

UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Linux)
    UPLOAD_PORT = /dev/ttyUSB0
endif
ifeq ($(UNAME_S),Darwin)
    UPLOAD_PORT = /dev/tty.wchusbserial1420
endif

UPLOAD_SPEED = 115200

#VERBOSE = 0
