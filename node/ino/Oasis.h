#ifndef Oasis_h
#define Oasis_h

// ***** DEBUG *****
//comment the line below to disable debug mode
#define DEBUG_ESP_OASIS

// ***** DEFINITIONS *****
// Use arduinojson.org/assistant to compute the capacity.
#define JSON_MEMORY_SIZE 1024
#define HOSTNAME_SIZE 15
#define SENSOR_COLLECT_DATA_PERIOD 180 //seconds
#define RETRY_CONNECTION_DELAY 5000 // ms
#define SERIAL_BAUDRATE 115200
#define OTA_PORT 8266


// Configuration that we'll store on disk
const char *CONFIG_FILE = "/config.json";

// ***** functions *****
int diffi(JsonVariant _base, JsonVariant _arrived);
const char* diffs(JsonVariant _base, JsonVariant _arrived);
void loadConfiguration();
void saveConfiguration(JsonDocument& CONFIG);
void mergeConfiguration(JsonDocument& base, JsonDocument& arrived);
void onMqttMessage(char* topic, byte* payload, unsigned int length);
void postResponse();
void mqttReconnect();
void setupWifi();
void setup();
void collectSensorData();
void loop();

#endif
