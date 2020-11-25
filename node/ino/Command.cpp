#include "Command.h"
using namespace std;

Command::Command(){
  /* order matters here */
  ACTION[IDX_ACTION_LIGHT]  = NODE::LIGHT;
  ACTION[IDX_ACTION_WATER] = NODE::WATER;
  ACTION[IDX_ACTION_FAN] = NODE::FAN;
  ACTION[IDX_ACTION_REBOOT] = NODE::REBOOT;
  ACTION[IDX_ACTION_RESET] = NODE::RESET;
}

void Command::updatePorts(State& state){
   state.getPin(PIN, ACTION, CMD_LENGTH);
}

void Command::logAction(int idx, const char* action, int pin, bool value){
  if( idx == IDX_ACTION_LIGHT ||
      idx == IDX_ACTION_WATER ||
      idx == IDX_ACTION_FAN){
    if(pin != PIN_NOT_CONFIGURED){
      Serial.printf("[COMMAND] %s[%d] = %d\r\n", action, pin, value);
    }else{
      Serial.printf("[COMMAND] %s not found\r\n", action);
    }
  }else{
    if(value){
      Serial.printf("[COMMAND] %sING\r\n", action);//VERB+ING
    }else{
      Serial.printf("[COMMAND] %s value not valid\r\n", action);
    }
  }
}

void Command::execute(State& state, JsonObject& cmd){
  for (int i = 0; i < CMD_LENGTH; i++) {
    if (!cmd[ACTION[i]].isNull()) {
      bool value =  cmd[ACTION[i]].as<bool>();
      logAction(i, ACTION[i], PIN[i], value);
      switch (i) {
        case IDX_ACTION_LIGHT:
        case IDX_ACTION_WATER:
        case IDX_ACTION_FAN:// ... all previous cases fall here
          if (PIN[i] != PIN_NOT_CONFIGURED){
            pinMode(PIN[i], OUTPUT);
            if(value){
              digitalWrite(PIN[i], HIGH);
            }else{
              digitalWrite(PIN[i], LOW);
            }
          }
          break;
        case IDX_ACTION_REBOOT:
          if(value){
            ESP.restart();
          }
          break;
        case IDX_ACTION_RESET:
          if(value){
          //state.remove();
            state.loadDefaultState();
          }
          break;
      }
    }
  }
}
