#include "Status.h"
using namespace std;

Status::Status(){
  /* order matters here */
  DEVICE[IDX_DEVICE_NODE]  = NODE::NODE;
  DEVICE[IDX_DEVICE_SOILX] = NODE::SOILX;
  DEVICE[IDX_DEVICE_SOIL1] = NODE::SOIL1;
  DEVICE[IDX_DEVICE_SOIL2] = NODE::SOIL2;
  DEVICE[IDX_DEVICE_SOIL3] = NODE::SOIL3;
  DEVICE[IDX_DEVICE_SOIL4] = NODE::SOIL4;
  DEVICE[IDX_DEVICE_DHT]   = NODE::DHT;
  DEVICE[IDX_DEVICE_LIGHT] = NODE::LIGHT;
  DEVICE[IDX_DEVICE_FAN]   = NODE::FAN;
  DEVICE[IDX_DEVICE_WATER] = NODE::WATER;
}

void Status::updatePorts(State& state){
   state.getPin(PIN, DEVICE, DEVICE_LENGTH);
}

void Status::logAction(int idx, const char* action, int pin, bool value){

}
/* user only for sensor ticker procedures */
void Status::collectForSensorTicket(State& state, JsonDocument& response){
  updatePorts(state);
  // compute the required size
  const size_t CAPACITY = JSON_ARRAY_SIZE(DEVICE_LENGTH);
  // allocate the memory for the document
  StaticJsonDocument<CAPACITY> doc;
  // create an empty array
  JsonArray devices = doc.to<JsonArray>();
  // add values
   for(int i = 0 ; i < DEVICE_LENGTH ; i++ ){
     devices.add(DEVICE[i]);
   }
  collect(state,devices,response);
}

void Status::collect(State& state, JsonArray& status, JsonDocument& response){
  updatePorts(state);
  JsonObject data = response.createNestedObject(NODE::DATA);
  for(JsonVariant s : status) {
    const char* device = s.as<char *>();
    if(strcmp(device, NODE::NODE) == 0){
      collectNodeData(state, data);
    } else if(strcmp(device, NODE::LIGHT) == 0){
      data[NODE::LIGHT] = state.getLightStatus();
    } else if(strcmp(device, NODE::FAN) == 0){
      data[NODE::FAN] = state.getFanStatus();
    } else if(strcmp(device, NODE::WATER) == 0){
      data[NODE::WATER] = state.getWaterStatus();
    } else if(strcmp(device, NODE::DHT) == 0){
      Serial.println("[STATUS] DHT !!!");
    } else if(strcmp(device, NODE::SOIL) == 0){
      Serial.println("[STATUS] SOIL !!!");
    }
  }
}

int Status::readDigitalInputPort(int port) {
  if(port == PIN_NOT_CONFIGURED){
    return PIN_NOT_CONFIGURED;
  }else{
    pinMode(port, INPUT);
    return digitalRead(port);
  }
}

void Status::collectNodeData(State& state, JsonObject& data){
  JsonObject node = data.createNestedObject(NODE::NODE);
  node[NODE::FREEHEAP] = ESP.getFreeHeap();
  node[NODE::FLASHID] = ESP.getFlashChipId();
  node[NODE::FLASHSIZE] = ESP.getFlashChipSize();
  node[NODE::SSID] = state.getSsid();
  node[NODE::MQTT_SERVER] = state.getMqttServer();
  node[NODE::MQTT_PORT] = state.getMqttPort();
  node[NODE::MQTT_TOPIC_INBOUND] = state.getMqttInboundTopic();
  node[NODE::MQTT_TOPIC_OUTBOUND] = state.getMqttOutboundTopic();
  node[NODE::SENSOR_COLLECT_DATA_PERIOD] = state.getSensorCollectDataPeriod();
  node[NODE::RETRY_WIFI_CONN_DELAY] = state.getWifiRetryConnectionDelay();
  node[NODE::SERIAL_BAUDRATE] = state.getSerialBaudRate();
  node[NODE::OTA_PORT] = state.getOtaPort();
  node[NODE::PIN] = state.getPinSetup();
}
