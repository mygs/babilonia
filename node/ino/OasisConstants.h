#ifndef OASISCONSTANTS_H
#define OASISCONSTANTS_H

//comment the line below to disable debug mode
#define DEBUG_ESP_OASIS
// Use arduinojson.org/assistant to compute the capacity.
#define JSON_MEMORY_SIZE 1024

namespace NODE {

  const char* CONFIG      = "CONFIG";
  const char* SSID        = "SSID";
  const char* PASSWORD    = "PASSWORD";
  const char* MQTT_SERVER = "MQTT_SERVER";
  const char* MQTT_PORT   = "MQTT_PORT";
  const char* MQTT_TOPIC_INBOUND = "MQTT_TOPIC_INBOUND";
  const char* MQTT_TOPIC_OUTBOUND = "MQTT_TOPIC_OUTBOUND";
  const char* SENSOR_COLLECT_DATA_PERIOD = "SENSOR_COLLECT_DATA_PERIOD";

  const char* RETRY_WIFI_CONN_DELAY = "RETRY_WIFI_CONN_DELAY";
  const char* SERIAL_BAUDRATE = "SERIAL_BAUDRATE";
  const char* OTA_PORT = "OTA_PORT";

  const char* PIN  = "PIN";
  const char* PIN0 = "0";
  const char* PIN1 = "1";
  const char* PIN2 = "2";
  const char* PIN3 = "3";
  const char* PIN4 = "4";
  const char* PIN5 = "5";
  const char* PIN6 = "6";
  const char* PIN7 = "7";
  const char* PIN8 = "8";

  const char* COMMAND = "COMMAND";
  const char* FAN     = "FAN";
  const char* WATER   = "WATER";
  const char* LIGHT   = "LIGHT";
  const char* REBOOT  = "REBOOT";
  const char* RESET   = "RESET";


  const char* STATUS  = "STATUS";
  const char* DHT     = "DHT";
  const char* SOIL1   = "SOIL.1";
  const char* SOIL2   = "SOIL.2";
  const char* SOIL3   = "SOIL.3";
  const char* SOIL4   = "SOIL.4";
  const char* SOILX   = "SOIL.X";

  const char* IDLE    = "IDLE";

}
#endif
