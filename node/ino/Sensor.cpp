#include "Sensor.h"
#include "OasisConstants.h"
using namespace std;

/* order matters here */
const char * Sensor::DEVICE[DEVICE_LENGTH] = {  NODE::NODE,
                                                NODE::SOIL,
                                                NODE::DHT,
                                                NODE::LIGHT,
                                                NODE::FAN,
                                                NODE::WATER};

Sensor::Sensor(){
}

void Sensor::updatePorts(State& state){
   state.getPin(PIN, DEVICE, DEVICE_LENGTH);
}

void Sensor::logAction(int idx, const char* action, int pin, bool value){

}

void Sensor::collect(State& state, JsonObject& cmd){
  updatePorts(state);

}
