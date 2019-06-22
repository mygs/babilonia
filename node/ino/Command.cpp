#include <Command.h>


void command(JsonDocument& currentState, JsonObject& command){
  for (int i = 0; i < 4; i++) {
    Serial.println("ACTION[i]");
  }
}
