#ifndef Command_h
#define Command_h
#include <Arduino.h>
#include <ArduinoJson.h>
//comment the line below to disable debug mode
#define DEBUG_ESP_OASIS
class Command {
private:
  static const char * ACTION[];
public:
  Command();
  void execute(JsonDocument& currentState, JsonObject& command);
};
#endif
