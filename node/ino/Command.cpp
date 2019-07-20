#include "Command.h"
#include "OasisConstants.h"
using namespace std;

/* order matters here */
const char * Command::ACTION[CMD_LENGTH] = {/*0*/  NODE::LIGHT,
                                            /*1*/  NODE::WATER,
                                            /*2*/  NODE::FAN,
                                            /*3*/  NODE::REBOOT,
                                            /*4*/  NODE::RESET};

Command::Command(){
}

void Command::updatePorts(State& state){
   state.getPin(PIN, ACTION, CMD_LENGTH);
}

void Command::logAction(int idx, const char* action, int pin, bool value){
  if( idx == 0 /*LIGHT*/ ||
      idx == 1 /*WATER*/ ||
      idx == 2 /*FAN*/){
    if(pin != -1){
      Serial.print("[COMMAND] ");
      Serial.print(action);
      Serial.print("[");
      Serial.print(pin);
      Serial.print("] = ");
      Serial.println(value);
    }else{
      Serial.print("[COMMAND] ");
      Serial.print(action);
      Serial.println(" not found");
    }
  }else{
    Serial.print("[COMMAND] ");
    Serial.print(action);
    if(value){
      Serial.println("ING"); //VERB+ING
    }else{
      Serial.println(" value not valid");
    }
  }
}

void Command::execute(State& state, JsonObject& cmd){
  updatePorts(state);
  for (int i = 0; i < CMD_LENGTH; i++) {
    if (!cmd[ACTION[i]].isNull()) {
      bool value =  cmd[ACTION[i]].as<bool>();
      logAction(i, ACTION[i], PIN[i], value);
      switch (i) {
        case 0: //LIGHT
        case 1: //WATER
        case 2: //FAN ... all previous cases fall here
          pinMode(PIN[i], OUTPUT);
          digitalWrite(PIN[i], value);
          break;
        case 3: //REBOOT
          if(value){
            ESP.restart();
          }
          break;
        case 4: //RESET
          if(value){
            state.remove();
          }
          break;
      }

    }
  }
}
