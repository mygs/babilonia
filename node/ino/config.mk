SKETCH = Oasis.ino

ESP_ROOT=$(BABILONIA_LIBS)/esp8266
ESP_LIBS=$(ESP_ROOT)/libraries

CUSTOM_LIBS =	$(BABILONIA_LIBS)/pubsubclient \
							$(BABILONIA_LIBS)/ArduinoJson/src

#Board type
BOARD = nodemcuv2

ESP_PORT = 8266

UPLOAD_SPEED = 115200
