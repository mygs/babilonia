#ifndef Command_h
#define Command_h
#include <Arduino.h>
#include <ArduinoJson.h>
#include "State.h"
#include "OasisConstants.h"

class Command {
private:
  const char * ACTION[CMD_LENGTH];
  int PIN[CMD_LENGTH];
  void updatePorts(State& state);
  void logAction(int idx, const char* action, int pin, bool value);
public:
  Command();
  void execute(State& state, JsonObject& cmd);
};
#endif
