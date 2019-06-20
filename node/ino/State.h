#ifndef State_h
#define State_h
#include <Arduino.h>
#include <ArduinoJson.h>
int diffi(JsonVariant _base, JsonVariant _arrived);
bool diffb(JsonVariant _base, JsonVariant _arrived);
const char* diffs(JsonVariant _base, JsonVariant _arrived);
#endif
