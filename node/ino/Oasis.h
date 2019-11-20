#ifndef Oasis_h
#define Oasis_h

// ***** DEFINITIONS *****
// Use arduinojson.org/assistant to compute the capacity.
#define JSON_MEMORY_SIZE 2048
#define HOSTNAME_SIZE 15
#define IP_SIZE 15
#define HEARTBEAT_MESSAGE_SIZE 64
#define MQTT_WILL_TOPIC 0
#define MQTT_WILL_QOS 0 //"fire and forget"
#define MQTT_WILL_RETAIN 0 //whether the will should be published with the retain flag (int : 0 or 1)
#define MQTT_WILL_MESSAGE 0

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
