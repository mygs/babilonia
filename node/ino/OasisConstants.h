#ifndef OASISCONSTANTS_H
#define OASISCONSTANTS_H

//comment the line below to disable debug mode
#define DEBUG_ESP_OASIS
// Use arduinojson.org/assistant to compute the capacity.
#define JSON_MEMORY_SIZE 1024

namespace NODE {

  char* CONFIG      = "CONFIG";
  char* SSID        = "SSID";
  char* PASSWORD    = "PASSWORD";
  char* MQTT_SERVER = "MQTT_SERVER";
  char* MQTT_PORT   = "MQTT_PORT";
  char* MQTT_TOPIC_INBOUND = "MQTT_TOPIC_INBOUND";
  char* MQTT_TOPIC_OUTBOUND = "MQTT_TOPIC_OUTBOUND";
  char* SENSOR_COLLECT_DATA_PERIOD = "SENSOR_COLLECT_DATA_PERIOD";

  char* RETRY_WIFI_CONN_DELAY = "RETRY_WIFI_CONN_DELAY";
  char* SERIAL_BAUDRATE = "SERIAL_BAUDRATE";
  char* OTA_PORT = "OTA_PORT";

  char* PIN  = "PIN";
  char* PIN0 = "0";
  char* PIN1 = "1";
  char* PIN2 = "2";
  char* PIN3 = "3";
  char* PIN4 = "4";
  char* PIN5 = "5";
  char* PIN6 = "6";
  char* PIN7 = "7";
  char* PIN8 = "8";

  char* COMMAND = "COMMAND";
  char* FAN     = "FAN";
  char* WATER   = "WATER";
  char* LIGHT   = "LIGHT";
  char* REBOOT  = "REBOOT";

  char* STATUS  = "STATUS";
  char* DHT     = "DHT";
  char* SOIL1   = "SOIL.1";
  char* SOIL2   = "SOIL.2";
  char* SOIL3   = "SOIL.3";
  char* SOIL4   = "SOIL.4";
  char* SOILX   = "SOIL.X";

  char* IDLE    = "IDLE";

}
#endif
