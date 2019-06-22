#ifndef State_h
#define State_h
#include <Arduino.h>
#include <ArduinoJson.h>

using namespace std;

//comment the line below to disable debug mode
#define DEBUG_ESP_OASIS
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

public:
  State();
  //get configuration
  const char * getMqttServer();
  int getMqttPort();
  int getSensorCollectDataPeriod();
  int getWifiRetryConnectionDelay();
  int getSerialBaudRate();
  int getOtaPort();
  const char * getMqttInboundTopic();
  const char * getMqttOutboundTopic();
  const char * getSsid();
  const char * getPassword();

  //procedures
  void loadState();
  void saveState(JsonDocument& newState);

  void remove();
  void print();
};
#endif
