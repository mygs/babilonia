#ifndef Oasis_h
#define Oasis_h

#define DEBUG_ESP_OASIS true
#define DEBUG_ESP_PORT Serial
#define DEBUG_OASIS(...) DEBUG_ESP_PORT.print( __VA_ARGS__ )

#define MQTT_SERVER "192.168.2.1"
#define MQTT_PORT 1883
#define MQTT_TOPIC_INBOUND "/oasis-inbound"
#define MQTT_TOPIC_OUTBOUND "/oasis-inbound"

#define OTA_PORT 8266

void onMqttMessage(char* topic, byte* payload, unsigned int length);
void mqttReconnect();
void setupWifi();
void setup();
void collectSensorData();
void loop();

#endif
