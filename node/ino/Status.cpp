#include "Status.h"
#include "OasisConstants.h"
using namespace std;

/* order matters here */
const char * Status::DEVICE[DEVICE_LENGTH] = {  NODE::NODE,
                                                NODE::SOILX,
                                                NODE::SOIL1,
                                                NODE::SOIL2,
                                                NODE::SOIL3,
                                                NODE::SOIL4,
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

void Status::collect(State& state, JsonArray& status, JsonDocument& response){
  updatePorts(state);
  JsonObject data = response.createNestedObject(NODE::DATA);
  for(JsonVariant s : status) {
    const char* device = s.as<char *>();
    if(strcmp(device, NODE::NODE) == 0){
      Serial.println("[STATUS] NODE !!!");
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
  //data[NODE::PASSWORD] = state.getPassword();
  data[NODE::MQTT_SERVER] = state.getMqttServer();
  data[NODE::MQTT_PORT] = state.getMqttPort();
  data[NODE::MQTT_TOPIC_INBOUND] = state.getMqttInboundTopic();
  data[NODE::MQTT_TOPIC_OUTBOUND] = state.getMqttOutboundTopic();
  data[NODE::SENSOR_COLLECT_DATA_PERIOD] = state.getSensorCollectDataPeriod();
  data[NODE::RETRY_WIFI_CONN_DELAY] = state.getWifiRetryConnectionDelay();
  data[NODE::SERIAL_BAUDRATE] = state.getSerialBaudRate();
  data[NODE::OTA_PORT] = state.getOtaPort();
  /*
  JsonObject statePIN    = state[NODE::PIN];
  JsonObject dataPIN = data.createNestedObject(NODE::PIN);

  dataPIN[NODE::PIN0] = statePIN[NODE::PIN0];
  dataPIN[NODE::PIN1] = statePIN[NODE::PIN1];
  dataPIN[NODE::PIN2] = statePIN[NODE::PIN2];
  dataPIN[NODE::PIN3] = statePIN[NODE::PIN3];
  dataPIN[NODE::PIN4] = statePIN[NODE::PIN4];
  dataPIN[NODE::PIN5] = statePIN[NODE::PIN5];
  dataPIN[NODE::PIN6] = statePIN[NODE::PIN6];
  dataPIN[NODE::PIN7] = statePIN[NODE::PIN7];
  dataPIN[NODE::PIN8] = statePIN[NODE::PIN8];
  */
}
