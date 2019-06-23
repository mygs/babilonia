#include "Command.h"
#include "OasisConstants.h"
using namespace std;

const char * Command::ACTION[CMD_LENGTH] = { NODE::LIGHT,
                                    NODE::WATER,
                                    NODE::FAN,
                                    NODE::REBOOT,
                                    NODE::RESET};

Command::Command(){
}

void Command::updatePorts(State& state){
   state.getPin(PIN, ACTION, CMD_LENGTH);
}

void Command::execute(State& state, JsonObject& cmd){
  updatePorts(state);
  for (int i = 0; i < CMD_LENGTH; i++) {
    if (!cmd[ACTION[i]].isNull()) {
      bool value =  cmd[ACTION[i]].as<bool>();
      switch (i) {
        case 0:
          Serial.print("[COMMAND] LIGHT[");
          Serial.print(PIN[0]);
          Serial.print("] = ");
          Serial.println(value);
          break;
        case 1:
          Serial.print("[COMMAND] WATER[");
          Serial.print(PIN[1]);
          Serial.print("] = ");
          Serial.println(value);
          break;
        case 2:
          Serial.print("[COMMAND] FAN[");
          Serial.print(PIN[2]);
          Serial.print("] = ");
          Serial.println(value);
          break;
        case 3:
          if(value){
            Serial.println("[COMMAND] REBOOT");
            ESP.restart();
          }
          break;
        case 4:
          if(value){
            Serial.println("[COMMAND] RESET");
            state.remove();
          }
          break;
      }

    }
  }
}
