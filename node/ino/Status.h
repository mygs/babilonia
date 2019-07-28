#ifndef Status_h
#define Status_h
#include <Arduino.h>
#include <ArduinoJson.h>
#include "State.h"
#include "OasisConstants.h"
#include "DHT.h"

class Status {
private:
  const char * DEVICE[DEVICE_LENGTH];
  int PIN[DEVICE_LENGTH];
  DHT* dht;
  void init();
  void logAction(int idx, const char* action, int pin, bool value);
  void collectNodeData(State& state, JsonObject& data);
  int readDigitalInputPort(int port);
  int checkPortConfiguration(int port, int status);
  void collectDHTData(JsonObject& data);
public:
  Status();
  void updatePorts(State& state);
  int devices(JsonArray& devices);
  void collect(State& state, JsonArray& status, JsonDocument& response);
  void collectForSensorTicket(State& state, JsonDocument& response);
};
#endif
