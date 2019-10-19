#include "Status.h"
using namespace std;

#define DHTTYPE DHT11

Status::Status(){
  init();
  dht = new DHT(PIN[IDX_DEVICE_DHT], DHTTYPE);
  dht->begin();
  capacitiveMoisture = new CapacitiveMoisture();
}

void Status::init(){
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
  DEVICE[IDX_DEVICE_CAPACITIVEMOISTURE] = NODE::CAPACITIVEMOISTURE;
}

void Status::updatePorts(State& state){
   state.getPin(PIN, DEVICE, DEVICE_LENGTH);
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
    } else if(strcmp(device, NODE::LIGHT) == 0){
      data[NODE::LIGHT] = checkPortConfiguration(PIN[IDX_DEVICE_LIGHT],state.getLightStatus());
    } else if(strcmp(device, NODE::FAN) == 0){
      data[NODE::FAN] = checkPortConfiguration(PIN[IDX_DEVICE_FAN],state.getFanStatus());
    } else if(strcmp(device, NODE::WATER) == 0){
      data[NODE::WATER] = checkPortConfiguration(PIN[IDX_DEVICE_WATER],state.getWaterStatus());
    } else if(strcmp(device, NODE::DHT) == 0){
      collectDHTData(data);
    } else if(strcmp(device, NODE::SOIL) == 0){
      Serial.println("[STATUS] SOIL !!!");
    } else if(strcmp(device, NODE::CAPACITIVEMOISTURE) == 0){
      collectCapacitiveMoistureData(data);
    }
  }
}

int Status::checkPortConfiguration(int port, int status) {
  if(port == PIN_NOT_CONFIGURED){
    return PIN_NOT_CONFIGURED;
  }else{
    return status;
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
  node[NODE::RETRY_WIFI_CONN_DELAY] = state.getWifiRetryConnectionDelay();
  node[NODE::SERIAL_BAUDRATE] = state.getSerialBaudRate();
  node[NODE::OTA_PORT] = state.getOtaPort();
  node[NODE::PIN] = state.getPinSetup();
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
  JsonObject capacitiveMoistureData = data.createNestedObject(NODE::CAPACITIVEMOISTURE);
  int m = capacitiveMoisture->read();
  if (isnan(m)) {
    char error_message[56]  = "[STATUS] Failed to read from Capacitive Moisture sensor";
    Serial.println(error_message);
    data[NODE::ERROR] = error_message;
  }else{
    capacitiveMoistureData[NODE::CAPACITIVEMOISTURE] = m;
  }
}
