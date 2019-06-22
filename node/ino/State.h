#ifndef State_h
#define State_h
#include <Arduino.h>
#include <ArduinoJson.h>
using namespace std;

//comment the line below to disable debug mode
#define DEBUG_ESP_OASIS

// State that we'll store on disk
#define STATE_FILE "/state.json"
// Use arduinojson.org/assistant to compute the capacity.
#define JSON_MEMORY_SIZE 1024

class State{
private:
  StaticJsonDocument<JSON_MEMORY_SIZE> currentState;
  int diffi(JsonVariant _base, JsonVariant _arrived);
  bool diffb(JsonVariant _base, JsonVariant _arrived);
  const char* diffs(JsonVariant _base, JsonVariant _arrived);
  void mergeState(JsonDocument& arrived);
  void saveDefaultState(JsonDocument& state);
  void loadDefaultState();
  void printFileSystemDetails();
public:
  State();
  void loadState();
  void saveState(JsonDocument& newState);
  const char * getMqttServer(){return currentState["CONFIG"]["MQTT_SERVER"];/*.as<char *>();*/}
  int getMqttPort(){return currentState["CONFIG"]["MQTT_PORT"].as<int>();}

  const char * getMqttInboundTopic(){return currentState["CONFIG"]["MQTT_TOPIC_INBOUND"];};
  const char * getMqttOutboundTopic(){return currentState["CONFIG"]["MQTT_TOPIC_OUTBOUND"];};
  const char * getSsid(){return currentState["CONFIG"]["SSID"];/*.as<char *>();*/}
  const char * getPassword(){return currentState["CONFIG"]["PASSWORD"];/*.as<char *>();*/}

};
#endif
