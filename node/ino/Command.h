#ifndef Command_h
#define Command_h
#include <Arduino.h>
#include <ArduinoJson.h>
//comment the line below to disable debug mode
#define DEBUG_ESP_OASIS

//extern String ACTION[] = {"LIGHT", "WATER", "FAN", "REBOOT"}; 

void command(JsonDocument& currentState, JsonObject& command);

#endif
