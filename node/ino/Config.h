#ifndef __CONFIG_H
#define __CONFIG_H

#define DEBUG_ESP_OASIS true
#define DEBUG_ESP_PORT Serial

#define DEBUG_OASIS(...) DEBUG_ESP_PORT.print( __VA_ARGS__ )

namespace Config
{
  const char* MQTT_SERVER = "192.168.2.1";
  const int MQTT_PORT = 1883;
  const int OTA_PORT = 8266;
}

#endif
