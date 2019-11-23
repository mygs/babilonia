#ifndef OASISCONSTANTS_H
#define OASISCONSTANTS_H

//comment the line below to disable debug mode
#define DEBUG_ESP_OASIS
// Use arduinojson.org/assistant to compute the capacity.
#define JSON_MEMORY_SIZE 1024

#define THRESHOLD_DISABLE_HEARTBEAT 999  // ~ 1 second
#define MIN_SENSOR_COLLECT_DATA_PERIOD 199  // ~ 1/5 second

#define DEVICE_LENGTH 10
#define IDX_DEVICE_NODE         0
#define IDX_DEVICE_SOILX        1
#define IDX_CHANNEL_SELECT_A    2
#define IDX_CHANNEL_SELECT_B    3
#define IDX_CHANNEL_SELECT_C    4
#define IDX_DEVICE_DHT          5
#define IDX_DEVICE_LIGHT        6
#define IDX_DEVICE_FAN          7
#define IDX_DEVICE_WATER        8
#define IDX_DEVICE_CAPACITIVEMOISTURE    9

#define CMD_LENGTH 5
#define IDX_ACTION_LIGHT    0
#define IDX_ACTION_WATER    1
#define IDX_ACTION_FAN      2
#define IDX_ACTION_REBOOT   3
#define IDX_ACTION_RESET    4

#define PIN_SIZE_DIGITAL 9
#define PIN_NOT_CONFIGURED -1

namespace NODE {
  extern const char* MESSAGE_ID;
  extern const char* NODE_ID;
  extern const char* NODE_IP;
  extern const char* FIRMWARE_VER;
  extern const char* ALL;
  extern const char* ERROR;
  extern const char* CONFIG;
  extern const char* SSID;
  extern const char* PASSWORD;
  extern const char* MQTT_SERVER;
  extern const char* MQTT_PORT;
  extern const char* MQTT_TOPIC_HEARTBEAT;
  extern const char* MQTT_TOPIC_INBOUND;
  extern const char* MQTT_TOPIC_OUTBOUND;
  extern const char* HEARTBEAT_PERIOD;
  extern const char* SENSOR_COLLECT_DATA_PERIOD;
  extern const char* RETRY_WIFI_CONN_DELAY;
  extern const char* SERIAL_BAUDRATE;
  extern const char* OTA_PORT;
  extern const char* PIN;
  extern const char* PINA;
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
  extern const char* TEMPERATURE;
  extern const char* HUMIDITY;
  extern const char* NODE;
  extern const char* SOIL;
  extern const char* SOILX;
  extern const char* WIND;
  extern const char* CHANNEL_SELECT_A;
  extern const char* CHANNEL_SELECT_B;
  extern const char* CHANNEL_SELECT_C;
  extern const char* CAPACITIVEMOISTURE;
  extern const char* IDLE;
  extern const char* FREEHEAP;
  extern const char* FLASHID;
  extern const char* FLASHSIZE;
  extern const char* MUX0;
  extern const char* MUX1;
  extern const char* MUX2;
  extern const char* MUX3;
  extern const char* MUX4;
  extern const char* MUX5;
  extern const char* MUX6;
  extern const char* MUX7;
}
#endif
