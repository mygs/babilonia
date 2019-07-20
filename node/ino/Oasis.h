#ifndef Oasis_h
#define Oasis_h

// ***** DEFINITIONS *****
// Use arduinojson.org/assistant to compute the capacity.
#define JSON_MEMORY_SIZE 1024
#define HOSTNAME_SIZE 15
#define HEARTBEAT_MESSAGE_SIZE 64

// ***** functions *****
void onMqttMessage(char* topic, byte* payload, unsigned int length);
void postResponse(const JsonDocument& message);
void mqttReconnect();
void setupWifi();
void setup();
void heartBeat();
void collectSensorData();
void loop();
#endif
