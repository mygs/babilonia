#ifndef Configuration_h
#define Configuration_h

#include <ArduinoJson.h>

class Configuration {
public:
  char *CONFIG_FILE;
  const char *SSID;
  const char *PASSWORD;
  const char *MQTT_SERVER;
  int MQTT_PORT;
  const char *MQTT_TOPIC_INBOUND;
  const char *MQTT_TOPIC_OUTBOUND;
  int PERIOD;
  const char *PIN0;
  const char *PIN1;
  const char *PIN2;
  const char *PIN3;
  const char *PIN4;
  const char *PIN5;
  const char *PIN6;
  const char *PIN7;
  const char *PIN8;
  Configuration();
  void saveConfiguration(JsonDocument& doc);
private:
  void saveDefaultConfiguration();
  void loadConfiguration();
  void copyFromJsonDocument(JsonDocument& doc);
};
#endif // ifndef Configuration_h
