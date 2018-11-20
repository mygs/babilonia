#ifndef Oasis_h
#define Oasis_h

// ***** DEBUG *****
#define DEBUG_ESP_OASIS true
#define DEBUG_ESP_PORT Serial
#define DEBUG_OASIS(...) DEBUG_ESP_PORT.print( __VA_ARGS__ )

// ***** DEFINITIONS *****
#define JSON_MEMORY_SIZE 200
#define HOSTNAME_SIZE 15
#define SENSOR_COLLECT_DATA_PERIOD 180 //seconds
#define RETRY_CONNECTION_DELAY 5000 // ms
#define SERIAL_BAUDRATE 115200
#define OTA_PORT 8266

// ***** MQTT *****
#define MQTT_SERVER "192.168.2.1"
#define MQTT_PORT 1883
#define MQTT_TOPIC_INBOUND "/oasis-inbound"
#define MQTT_TOPIC_OUTBOUND "/oasis-outbound"

// ***** functions *****
void onMqttMessage(char* topic, byte* payload, unsigned int length);
void mqttReconnect();
void setupWifi();
void setup();
void collectSensorData();
void loop();

#endif
