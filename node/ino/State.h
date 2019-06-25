#ifndef State_h
#define State_h
#include <Arduino.h>
#include <ArduinoJson.h>

using namespace std;

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
  int getHeartBeatPeriod();
  int getSensorCollectDataPeriod();
  int getWifiRetryConnectionDelay();
  int getSerialBaudRate();
  int getOtaPort();
  const char * getMqttInboundTopic();
  const char * getMqttOutboundTopic();
  const char * getSsid();
  const char * getPassword();
  JsonObject getPinSetup();

  //procedures
  void load();
  void save(JsonDocument& newState);

  void remove();
  void print();
  void getPin(int pin[], const char* ACTION[], int length);
};
#endif
