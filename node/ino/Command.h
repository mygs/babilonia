#ifndef Command_h
#define Command_h
#include <Arduino.h>
#include <ArduinoJson.h>
#include "State.h"

#define CMD_LENGTH 5

class Command {
private:
  static const char * ACTION[CMD_LENGTH];
  int PIN[CMD_LENGTH];
  void updatePorts(State& state);
  void logAction(int idx, const char* action, int pin, bool value);
public:
  Command();
  void execute(State& state, JsonObject& cmd);
};
#endif
