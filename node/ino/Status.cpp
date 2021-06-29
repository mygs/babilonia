#include "Status.h"
using namespace std;

#define DHTTYPE DHT11

Status::Status(){
  init();
}

void Status::init(){
  /* order matters here */
  DEVICE[IDX_DEVICE_NODE]  = NODE::NODE;
  DEVICE[IDX_DEVICE_SOILX] = NODE::SOILX;//TODO: REMOVEME
  DEVICE[IDX_CHANNEL_SELECT_A] = NODE::CHANNEL_SELECT_A;
  DEVICE[IDX_CHANNEL_SELECT_B] = NODE::CHANNEL_SELECT_B;
  DEVICE[IDX_CHANNEL_SELECT_C] = NODE::CHANNEL_SELECT_C;
  DEVICE[IDX_DEVICE_DHT]   = NODE::DHT;
  DEVICE[IDX_DEVICE_LIGHT] = NODE::LIGHT;
  DEVICE[IDX_DEVICE_FAN]   = NODE::FAN;
  DEVICE[IDX_DEVICE_WATER] = NODE::WATER;
  DEVICE[IDX_DEVICE_CAPACITIVEMOISTURE] = NODE::CAPACITIVEMOISTURE;
  DEVICE[IDX_DEVICE_SWITCH_A] = NODE::SWITCH_A;
  DEVICE[IDX_DEVICE_SWITCH_B] = NODE::SWITCH_B;

}

void Status::updatePorts(State& state){
   state.getPin(PIN, DEVICE, DEVICE_LENGTH);
   initialiseSensors();
}

void Status::initialiseSensors(){
  delete dht;
  delete capacitiveMoisture;
  dht = new DHT(PIN[IDX_DEVICE_DHT], DHTTYPE);
  dht->begin();
  capacitiveMoisture = new CapacitiveMoisture();
}

void Status::logAction(int idx, const char* action, int pin, bool value){

}
/* user only for sensor ticker procedures */
void Status::collectForSensorTicket(State& state, JsonDocument& response){
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
  JsonObject data = response.createNestedObject(NODE::DATA);
  for(JsonVariant s : status) {
    const char* device = s.as<char *>();
    if(strcmp(device, NODE::NODE) == 0){
      collectNodeData(state, data);
    } else if(checkDev(device, NODE::CAPACITIVEMOISTURE, PIN[IDX_DEVICE_CAPACITIVEMOISTURE])){
      collectCapacitiveMoistureData(data);
    } else if(checkDev(device, NODE::LIGHT, PIN[IDX_DEVICE_LIGHT])){
      data[NODE::LIGHT] = state.getLightStatus();
    } else if(checkDev(device, NODE::FAN, PIN[IDX_DEVICE_FAN])){
      data[NODE::FAN] = state.getFanStatus();
    } else if(checkDev(device, NODE::WATER, PIN[IDX_DEVICE_WATER])){
      data[NODE::WATER] = state.getWaterStatus();
    } else if(checkDev(device, NODE::DHT, PIN[IDX_DEVICE_DHT])){
      collectDHTData(data);
    } else if(checkDev(device, NODE::SOIL, PIN[IDX_DEVICE_SOILX])){
      Serial.println("[STATUS] SOIL !!!");
    } else if(checkDev(device, NODE::SWITCH_A, PIN[IDX_DEVICE_SWITCH_A])){
      data[NODE::SWITCH_A] = state.getSwitchAStatus();
    } else if(checkDev(device, NODE::SWITCH_B, PIN[IDX_DEVICE_SWITCH_B])){
      data[NODE::SWITCH_B] = state.getSwitchBStatus();
    }
  }
}

bool Status::checkDev(const char* devA, const char* devB, int port){
  return strcmp(devA, devB) == 0 && port != PIN_NOT_CONFIGURED;
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
  node[NODE::FIRMWARE_VER] = FIRMWARE_VERSION;
  node[NODE::FREEHEAP] = ESP.getFreeHeap();
  node[NODE::FLASHID] = ESP.getFlashChipId();
  node[NODE::FLASHSIZE] = ESP.getFlashChipSize();
  node[NODE::SSID] = state.getSsid();
  node[NODE::MQTT_SERVER] = state.getMqttServer();
  node[NODE::MQTT_PORT] = state.getMqttPort();
  node[NODE::MQTT_TOPIC_INBOUND] = state.getMqttInboundTopic();
  node[NODE::MQTT_TOPIC_OUTBOUND] = state.getMqttOutboundTopic();
  node[NODE::SENSOR_COLLECT_DATA_PERIOD] = state.getSensorCollectDataPeriod();
  node[NODE::HEARTBEAT_PERIOD] = state.getHeartBeatPeriod();
  node[NODE::RETRY_WIFI_CONN_DELAY] = state.getWifiRetryConnectionDelay();
  node[NODE::SERIAL_BAUDRATE] = state.getSerialBaudRate();
  node[NODE::OTA_PORT] = state.getOtaPort();
  node[NODE::PIN] = state.getPinSetup();
  node[NODE::BOOT] = state.getBootCount();
}


void Status::collectDHTData(JsonObject& data){
  JsonObject dhtData = data.createNestedObject(NODE::DHT);
  // Reading temperature or humidity takes about 250 milliseconds!
  // Sensor readings may also be up to 2 seconds 'old' (its a very slow sensor)
  float h = dht->readHumidity();
  // Read temperature as Celsius (the default)
  float t = dht->readTemperature();
  // Compute heat index in Celsius (isFahreheit = false)
  // TODO: float hic = dht.computeHeatIndex(t, h, false);
  // Check if any reads failed and exit early (to try again).
  if (isnan(h) || isnan(t)) {
    char error_message[42]  = "[STATUS] Failed to read from DHT sensor";
    Serial.println(error_message);
    data[NODE::ERROR] = error_message;
  }else{
    dhtData[NODE::TEMPERATURE] = t;
    dhtData[NODE::HUMIDITY] = h;
  }

}

void Status::collectCapacitiveMoistureData(JsonObject& data){
  JsonObject moistureData = data.createNestedObject(NODE::CAPACITIVEMOISTURE);
  moistureData[NODE::MUX0] = capacitiveMoisture->read(PIN, 0);
  moistureData[NODE::MUX1] = capacitiveMoisture->read(PIN, 1);
  moistureData[NODE::MUX2] = capacitiveMoisture->read(PIN, 2);
  moistureData[NODE::MUX3] = capacitiveMoisture->read(PIN, 3);
  moistureData[NODE::MUX4] = capacitiveMoisture->read(PIN, 4);
  moistureData[NODE::MUX5] = capacitiveMoisture->read(PIN, 5);
  moistureData[NODE::MUX6] = capacitiveMoisture->read(PIN, 6);
  moistureData[NODE::MUX7] = capacitiveMoisture->read(PIN, 7);
}
