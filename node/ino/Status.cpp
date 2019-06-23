#include "Status.h"
#include "OasisConstants.h"
using namespace std;

/* order matters here */
const char * Status::DEVICE[DEVICE_LENGTH] = {  NODE::NODE,
                                                NODE::SOIL,
                                                NODE::DHT,
                                                NODE::LIGHT,
                                                NODE::FAN,
                                                NODE::WATER};

Status::Status(){
}

void Status::updatePorts(State& state){
   state.getPin(PIN, DEVICE, DEVICE_LENGTH);
}

void Status::logAction(int idx, const char* action, int pin, bool value){

}

void Status::collect(State& state, JsonArray& status){
  updatePorts(state);
  for(JsonVariant s : status) {
    Serial.print("[STATUS] ");
    Serial.println(s.as<char *>());
  }
}
