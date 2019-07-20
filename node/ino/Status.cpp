#include "Status.h"
#include "OasisConstants.h"
using namespace std;

/* order matters here */
const char * Status::DEVICE[DEVICE_LENGTH] = {/*0*/    NODE::NODE,
                                              /*1*/    NODE::SOILX,
                                              /*2*/    NODE::SOIL1,
                                              /*3*/    NODE::SOIL2,
                                              /*4*/    NODE::SOIL3,
                                              /*5*/    NODE::SOIL4,
                                              /*6*/    NODE::DHT,
                                              /*7*/    NODE::LIGHT,
                                              /*8*/    NODE::FAN,
                                              /*9*/    NODE::WATER};

Status::Status(){
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
      Serial.println("[STATUS] LIGHT !!!");
    } else if(strcmp(device, NODE::FAN) == 0){
      Serial.println("[STATUS] FAN !!!");
    } else if(strcmp(device, NODE::WATER) == 0){
      Serial.println("[STATUS] WATER !!!");
    } else if(strcmp(device, NODE::DHT) == 0){
      Serial.println("[STATUS] DHT !!!");
    } else if(strcmp(device, NODE::SOIL) == 0){
      Serial.println("[STATUS] SOIL !!!");
    }
  }
}

void Status::collectNodeData(State& state, JsonObject& data){
  data[NODE::FREEHEAP] = ESP.getFreeHeap();
  data[NODE::FLASHID] = ESP.getFlashChipId();
  data[NODE::FLASHSIZE] = ESP.getFlashChipSize();
  data[NODE::SSID] = state.getSsid();
  data[NODE::MQTT_SERVER] = state.getMqttServer();
  data[NODE::MQTT_PORT] = state.getMqttPort();
  data[NODE::MQTT_TOPIC_INBOUND] = state.getMqttInboundTopic();
  data[NODE::MQTT_TOPIC_OUTBOUND] = state.getMqttOutboundTopic();
  data[NODE::SENSOR_COLLECT_DATA_PERIOD] = state.getSensorCollectDataPeriod();
  data[NODE::RETRY_WIFI_CONN_DELAY] = state.getWifiRetryConnectionDelay();
  data[NODE::SERIAL_BAUDRATE] = state.getSerialBaudRate();
  data[NODE::OTA_PORT] = state.getOtaPort();
  data[NODE::PIN] = state.getPinSetup();
}
