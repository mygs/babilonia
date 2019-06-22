#include <Command.h>
using namespace std;

const char * Command::ACTION[4] = {"LIGHT", "WATER", "FAN", "REBOOT"};

Command::Command(){
}

void Command::execute(JsonDocument& currentState, JsonObject& command){
  for (int i = 0; i < 4; i++) {
    Serial.println(ACTION[i]);
  }
}
