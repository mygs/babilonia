#include "Command.h"
#include "OasisConstants.h"
using namespace std;

const char * Command::ACTION[5] = { NODE::LIGHT,
                                    NODE::WATER,
                                    NODE::FAN,
                                    NODE::REBOOT,
                                    NODE::RESET};

Command::Command(){
}

void Command::execute(State& state, JsonObject& cmd){
  for (int i = 0; i < CMD_LENGTH; i++) {
    if (!cmd[ACTION[i]].isNull()) {
      bool value =  cmd[ACTION[i]].as<bool>();
      switch (i) {
        case 0:
          Serial.print("[COMMAND] SWITCH LIGHT = ");
          break;
        case 1:
          Serial.print("[COMMAND] SWITCH WATER = ");
          break;
        case 2:
          Serial.print("[COMMAND] SWITCH FAN = ");
          break;
        case 3:
          Serial.print("[COMMAND] SWITCH REBOOT = ");
          break;
        case 4:
          Serial.print("[COMMAND] SWITCH RESET = ");
          break;
      }
      Serial.println(value);
    }
  }
}
