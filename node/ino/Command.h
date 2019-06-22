#ifndef Command_h
#define Command_h
#include <Arduino.h>
#include <ArduinoJson.h>
//comment the line below to disable debug mode
#define DEBUG_ESP_OASIS
using namespace std;

namespace Command {
  void execute(JsonDocument& currentState, JsonObject& command);
}
#endif
