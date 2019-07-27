#ifndef OASISCONSTANTS_H
#define OASISCONSTANTS_H

//comment the line below to disable debug mode
#define DEBUG_ESP_OASIS
// Use arduinojson.org/assistant to compute the capacity.
#define JSON_MEMORY_SIZE 1024

#define DEVICE_LENGTH 10
#define IDX_DEVICE_NODE   0
#define IDX_DEVICE_SOILX  1
#define IDX_DEVICE_SOIL1  2
#define IDX_DEVICE_SOIL2  3
#define IDX_DEVICE_SOIL3  4
#define IDX_DEVICE_SOIL4  5
#define IDX_DEVICE_DHT    6
#define IDX_DEVICE_LIGHT  7
#define IDX_DEVICE_FAN    8
#define IDX_DEVICE_WATER  9

#define CMD_LENGTH 5
#define IDX_ACTION_LIGHT   0
#define IDX_ACTION_WATER  1
#define IDX_ACTION_FAN  2
#define IDX_ACTION_REBOOT  3
#define IDX_ACTION_RESET  4

#define PIN_SIZE 9
#define PIN_NOT_CONFIGURED -1

namespace NODE {
  extern const char* MESSAGE_ID;
  extern const char* NODE_ID;
  extern const char* ALL;
  extern const char* ERROR;
  extern const char* CONFIG;
  extern const char* SSID;
  extern const char* PASSWORD;
  extern const char* MQTT_SERVER;
  extern const char* MQTT_PORT;
  extern const char* MQTT_TOPIC_INBOUND;
  extern const char* MQTT_TOPIC_OUTBOUND;
  extern const char* HEARTBEAT_PERIOD;
  extern const char* SENSOR_COLLECT_DATA_PERIOD;
  extern const char* RETRY_WIFI_CONN_DELAY;
  extern const char* SERIAL_BAUDRATE;
  extern const char* OTA_PORT;
  extern const char* PIN;
  extern const char* PIN0;
  extern const char* PIN1;
  extern const char* PIN2;
  extern const char* PIN3;
  extern const char* PIN4;
  extern const char* PIN5;
  extern const char* PIN6;
  extern const char* PIN7;
  extern const char* PIN8;
  extern const char* COMMAND;
  extern const char* FAN;
  extern const char* WATER;
  extern const char* LIGHT;
  extern const char* REBOOT;
  extern const char* RESET;
  extern const char* DATA;
  extern const char* STATUS;
  extern const char* DHT;
  extern const char* NODE;
  extern const char* SOIL;
  extern const char* SOIL1;
  extern const char* SOIL2;
  extern const char* SOIL3;
  extern const char* SOIL4;
  extern const char* SOILX;
  extern const char* IDLE;
  extern const char* FREEHEAP;
  extern const char* FLASHID;
  extern const char* FLASHSIZE;
}
#endif
