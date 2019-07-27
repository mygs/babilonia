#ifndef Status_h
#define Status_h
#include <Arduino.h>
#include <ArduinoJson.h>
#include "State.h"
#include "OasisConstants.h"

class Status {
private:
  const char * DEVICE[DEVICE_LENGTH];
  int PIN[DEVICE_LENGTH];
  void updatePorts(State& state);
  void logAction(int idx, const char* action, int pin, bool value);
  void collectNodeData(State& state, JsonObject& data);
  int readDigitalPort(int port);
public:
  Status();
  int devices(JsonArray& devices);
  void collect(State& state, JsonArray& status, JsonDocument& response);
  void collectForSensorTicket(State& state, JsonDocument& response);
};
#endif