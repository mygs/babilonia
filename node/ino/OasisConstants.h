#ifndef OASISCONSTANTS_H
#define OASISCONSTANTS_H

//comment the line below to disable debug mode
#define DEBUG_ESP_OASIS
// Use arduinojson.org/assistant to compute the capacity.
#define JSON_MEMORY_SIZE 1024

namespace NODE {

  extern const char* CONFIG;
  extern const char* SSID;
  extern const char* PASSWORD;
  extern const char* MQTT_SERVER;
  extern const char* MQTT_PORT;
  extern const char* MQTT_TOPIC_INBOUND;
  extern const char* MQTT_TOPIC_OUTBOUND;
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


  extern const char* STATUS;
  extern const char* DHT;
  extern const char* SOIL1;
  extern const char* SOIL2;
  extern const char* SOIL3;
  extern const char* SOIL4;
  extern const char* SOILX;

  extern const char* IDLE;

}
#endif
