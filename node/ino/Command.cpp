#include <Command.h>

char * ACTION[] = {"LIGHT", "WATER", "FAN", "REBOOT"};

void Command::execute(JsonDocument& currentState, JsonObject& command){
  for (int i = 0; i < 4; i++) {
    Serial.println(ACTION[i]);
  }
}
