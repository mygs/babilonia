#ifndef State_h
#define State_h
#include <Arduino.h>
#include <ArduinoJson.h>

//comment the line below to disable debug mode
#define DEBUG_ESP_OASIS

// State that we'll store on disk
#define STATE_FILE "/state.json"

int diffi(JsonVariant _base, JsonVariant _arrived);
bool diffb(JsonVariant _base, JsonVariant _arrived);
const char* diffs(JsonVariant _base, JsonVariant _arrived);
void mergeState(JsonDocument& base, JsonDocument& arrived);
void loadDefaultState(JsonDocument& state);
void saveState(JsonDocument& currentState, JsonDocument& newState);
void loadState(JsonDocument& state);
void saveDefaultState(JsonDocument& state);
#endif
