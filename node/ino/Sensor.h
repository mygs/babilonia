#ifndef Sensor_h
#define Sensor_h
#include <Arduino.h>
#include <ArduinoJson.h>
#include "State.h"
//comment the line below to disable debug mode
#define DEBUG_ESP_OASIS
#define DEVICES_LENGTH 6
class Sensor {
private:
  static const char * DEVICE[DEVICES_LENGTH];
  int PIN[DEVICES_LENGTH];
  void updatePorts(State& state);
  void logAction(int idx, const char* action, int pin, bool value);
public:
  Sensor();
  void collect(State& state, JsonObject& cmd);
};
#endif
