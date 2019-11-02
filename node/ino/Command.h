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
  void logAction(int idx, const char* action, int pin, bool value);
public:
  Command();
  Command(State& state);
  void updatePorts(State& state);
  void execute(State& state, JsonObject& cmd);
};
#endif
