#ifndef State_h
#define State_h
#include <Arduino.h>
#include <ArduinoJson.h>
using namespace std;

//comment the line below to disable debug mode
#define DEBUG_ESP_OASIS

// State that we'll store on disk
#define STATE_FILE "/state.json"

class State{
private:
  int diffi(JsonVariant _base, JsonVariant _arrived);
  bool diffb(JsonVariant _base, JsonVariant _arrived);
  const char* diffs(JsonVariant _base, JsonVariant _arrived);
  void mergeState(JsonDocument& base, JsonDocument& arrived);
public:
  State();
  void loadDefaultState(JsonDocument& state);
  void loadState(JsonDocument& state);
  void saveState(JsonDocument& currentState, JsonDocument& newState);
  void saveDefaultState(JsonDocument& state);
  void printFileSystemDetails();
};
#endif
