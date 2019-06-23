#ifndef Status_h
#define Status_h
#include <Arduino.h>
#include <ArduinoJson.h>
#include "State.h"
//comment the line below to disable debug mode
#define DEBUG_ESP_OASIS
#define DEVICE_LENGTH 6
class Status {
private:
  static const char * DEVICE[DEVICE_LENGTH];
  int PIN[DEVICE_LENGTH];
  void updatePorts(State& state);
  void logAction(int idx, const char* action, int pin, bool value);
public:
  Status();
  void collect(State& state, JsonArray& status);
};
#endif
