#ifndef Oasis_h
#define Oasis_h

// ***** DEBUG *****
//comment the line below to disable debug mode
#define DEBUG_ESP_OASIS

// ***** DEFINITIONS *****
// Use arduinojson.org/assistant to compute the capacity.
#define JSON_MEMORY_SIZE 1024
#define HOSTNAME_SIZE 15

// ***** functions *****
void onMqttMessage(char* topic, byte* payload, unsigned int length);
void postResponse();
void mqttReconnect();
void setupWifi();
void setup();
void collectSensorData();
void loop();
#endif
