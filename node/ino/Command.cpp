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

void Command::execute(State& state, JsonObject& command){
  for (int i = 0; i < 5; i++) {
    Serial.print("[COMMAND] ");
    Serial.println(ACTION[i]);

  }
}
