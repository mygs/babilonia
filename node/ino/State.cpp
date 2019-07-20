#include "State.h"
#include <FS.h> // Include the SPIFFS library
#include "InitialConfiguration.h"
#include "OasisConstants.h"

State::State(){
  if (!SPIFFS.begin()) {
      Serial.println("Failed to mount file system");
  }
}

const char * State::getMqttServer(){
  return currentState[NODE::CONFIG][NODE::MQTT_SERVER];
}

int State::getHeartBeatPeriod(){
  return currentState[NODE::CONFIG][NODE::HEARTBEAT_PERIOD].as<int>();
}

int State::getSensorCollectDataPeriod(){
  return currentState[NODE::CONFIG][NODE::SENSOR_COLLECT_DATA_PERIOD].as<int>();
}

int State::getWifiRetryConnectionDelay(){
  return currentState[NODE::CONFIG][NODE::RETRY_WIFI_CONN_DELAY].as<int>();
}

int State::getSerialBaudRate(){
  return currentState[NODE::CONFIG][NODE::SERIAL_BAUDRATE].as<int>();
}

int State::getOtaPort(){
  return currentState[NODE::CONFIG][NODE::OTA_PORT].as<int>();
}

int State::getMqttPort(){
  return currentState[NODE::CONFIG][NODE::MQTT_PORT].as<int>();
}

const char * State::getMqttInboundTopic(){
  return currentState[NODE::CONFIG][NODE::MQTT_TOPIC_INBOUND];
}

const char * State::getMqttOutboundTopic(){
  return currentState[NODE::CONFIG][NODE::MQTT_TOPIC_OUTBOUND];
}

const char * State::getSsid(){
  return currentState[NODE::CONFIG][NODE::SSID];
}

const char * State::getPassword(){
  return currentState[NODE::CONFIG][NODE::PASSWORD];
}

JsonObject State::getPinSetup(){
  return currentState[NODE::CONFIG][NODE::PIN];
}

const char* State::diffs(JsonVariant _base, JsonVariant _arrived) {
  const char *arrived = _arrived.as<char *>();
  if ((arrived != NULL) && (arrived[0] != '\0')) {
    return arrived;
  } else {
    return _base.as<char *>();
  }
}

int State::diffi(JsonVariant _base, JsonVariant _arrived) {
  int arrived = _arrived.as<int>();
  if (arrived >= 0) {
    return arrived;
  } else {
    return _base.as<int>();
  }
}

bool State::diffb(JsonVariant _base, JsonVariant _arrived) {
  if (!_arrived.isNull()) {
    return _arrived.as<bool>();
  } else {
    return _base.as<bool>();
  }
}

// Merge state
void State::mergeState(JsonDocument& arrived) {

  JsonObject arrivedConfig = arrived[NODE::CONFIG];

  if(!arrivedConfig.isNull()){
    JsonObject baseConfig = currentState[NODE::CONFIG];

    baseConfig[NODE::SSID]        = diffs(baseConfig[NODE::SSID], arrivedConfig[NODE::SSID]);
    baseConfig[NODE::PASSWORD]    = diffs(baseConfig[NODE::PASSWORD], arrivedConfig[NODE::PASSWORD]);
    baseConfig[NODE::MQTT_SERVER] = diffs(baseConfig[NODE::MQTT_SERVER], arrivedConfig[NODE::MQTT_SERVER]);
    baseConfig[NODE::MQTT_PORT]   = diffi(baseConfig[NODE::MQTT_PORT],
                                arrivedConfig[NODE::MQTT_PORT]);
    baseConfig[NODE::MQTT_TOPIC_INBOUND] =
      diffs(baseConfig[NODE::MQTT_TOPIC_INBOUND],  arrivedConfig[NODE::MQTT_TOPIC_INBOUND]);
    baseConfig[NODE::MQTT_TOPIC_OUTBOUND] =
      diffs(baseConfig[NODE::MQTT_TOPIC_OUTBOUND], arrivedConfig[NODE::MQTT_TOPIC_OUTBOUND]);
    baseConfig[NODE::HEARTBEAT_PERIOD] = diffi(currentState[NODE::HEARTBEAT_PERIOD],
         arrivedConfig[NODE::HEARTBEAT_PERIOD]);
    baseConfig[NODE::SENSOR_COLLECT_DATA_PERIOD] = diffi(currentState[NODE::SENSOR_COLLECT_DATA_PERIOD],
       arrivedConfig[NODE::SENSOR_COLLECT_DATA_PERIOD]);

    baseConfig[NODE::RETRY_WIFI_CONN_DELAY]   = diffi(baseConfig[NODE::RETRY_WIFI_CONN_DELAY],
                                   arrivedConfig[NODE::RETRY_WIFI_CONN_DELAY]);
    baseConfig[NODE::SERIAL_BAUDRATE]   = diffi(baseConfig[NODE::SERIAL_BAUDRATE],
                                   arrivedConfig[NODE::SERIAL_BAUDRATE]);
    baseConfig[NODE::OTA_PORT]   = diffi(baseConfig[NODE::OTA_PORT],
                                  arrivedConfig[NODE::OTA_PORT]);
    JsonObject arrivedPIN = arrivedConfig[NODE::PIN];
    if(!arrivedPIN.isNull()){
      JsonObject basePIN    = baseConfig[NODE::PIN];

      basePIN[NODE::PIN0] = diffs(basePIN[NODE::PIN0], arrivedPIN[NODE::PIN0]);
      basePIN[NODE::PIN1] = diffs(basePIN[NODE::PIN1], arrivedPIN[NODE::PIN1]);
      basePIN[NODE::PIN2] = diffs(basePIN[NODE::PIN2], arrivedPIN[NODE::PIN2]);
      basePIN[NODE::PIN3] = diffs(basePIN[NODE::PIN3], arrivedPIN[NODE::PIN3]);
      basePIN[NODE::PIN4] = diffs(basePIN[NODE::PIN4], arrivedPIN[NODE::PIN4]);
      basePIN[NODE::PIN5] = diffs(basePIN[NODE::PIN5], arrivedPIN[NODE::PIN5]);
      basePIN[NODE::PIN6] = diffs(basePIN[NODE::PIN6], arrivedPIN[NODE::PIN6]);
      basePIN[NODE::PIN7] = diffs(basePIN[NODE::PIN7], arrivedPIN[NODE::PIN7]);
      basePIN[NODE::PIN8] = diffs(basePIN[NODE::PIN8], arrivedPIN[NODE::PIN8]);
    }
  }

  JsonObject arrivedCommand = arrived[NODE::COMMAND];
  if(!arrivedCommand.isNull()){
    JsonObject baseCommand = currentState[NODE::COMMAND];

    baseCommand[NODE::LIGHT] = diffb(baseCommand[NODE::LIGHT], arrivedCommand[NODE::LIGHT]);
    baseCommand[NODE::FAN] = diffb(baseCommand[NODE::FAN], arrivedCommand[NODE::FAN]);
    baseCommand[NODE::WATER] = diffb(baseCommand[NODE::WATER], arrivedCommand[NODE::WATER]);
  }
}
void State::loadDefaultState(){
  currentState.clear();
  JsonObject CONFIG = currentState.createNestedObject(NODE::CONFIG);
  CONFIG[NODE::SSID]                = InitialConfiguration::SSID;
  CONFIG[NODE::PASSWORD]            = InitialConfiguration::PASSWORD;
  CONFIG[NODE::MQTT_SERVER]         = InitialConfiguration::MQTT_SERVER;
  CONFIG[NODE::MQTT_PORT]           = InitialConfiguration::MQTT_PORT;
  CONFIG[NODE::MQTT_TOPIC_INBOUND]  = InitialConfiguration::MQTT_TOPIC_INBOUND;
  CONFIG[NODE::MQTT_TOPIC_OUTBOUND] = InitialConfiguration::MQTT_TOPIC_OUTBOUND;
  CONFIG[NODE::HEARTBEAT_PERIOD]    = InitialConfiguration::HEARTBEAT_PERIOD;
  CONFIG[NODE::SENSOR_COLLECT_DATA_PERIOD] = InitialConfiguration::SENSOR_COLLECT_DATA_PERIOD;
  CONFIG[NODE::RETRY_WIFI_CONN_DELAY] = InitialConfiguration::RETRY_WIFI_CONN_DELAY;
  CONFIG[NODE::SERIAL_BAUDRATE] = InitialConfiguration::SERIAL_BAUDRATE;
  CONFIG[NODE::OTA_PORT] = InitialConfiguration::OTA_PORT;

  JsonObject PIN = CONFIG.createNestedObject(NODE::PIN);
  PIN[NODE::PIN0] = InitialConfiguration::PIN0;
  PIN[NODE::PIN1] = InitialConfiguration::PIN1;
  PIN[NODE::PIN2] = InitialConfiguration::PIN2;
  PIN[NODE::PIN3] = InitialConfiguration::PIN3;
  PIN[NODE::PIN4] = InitialConfiguration::PIN4;
  PIN[NODE::PIN5] = InitialConfiguration::PIN5;
  PIN[NODE::PIN6] = InitialConfiguration::PIN6;
  PIN[NODE::PIN7] = InitialConfiguration::PIN7;
  PIN[NODE::PIN8] = InitialConfiguration::PIN8;

  JsonObject COMMAND = currentState.createNestedObject(NODE::COMMAND);
  COMMAND[NODE::LIGHT] = false;
  COMMAND[NODE::FAN] = false;
  COMMAND[NODE::WATER] = false;

  Serial.println("[STATE] creating default file");
  saveDefaultState(currentState);

}

// Save State to a file
void State::saveDefaultState(JsonDocument& state) {
  if (SPIFFS.exists(STATE_FILE)) {
    Serial.println("[STATE] Removing existing file");
    SPIFFS.remove(STATE_FILE);
  }

  File file = SPIFFS.open(STATE_FILE, "w");

  if (!file) {
    Serial.println("[STATE] Failed to create file");
    return;
  } else {
    Serial.println("[STATE] Saving");
    if (serializeJson(state, file) == 0) {
      Serial.println("[STATE] Failed to write file");
    }
    file.close();
  }
}

// Save State to a file
void State::save(JsonDocument& newState) {
  if (SPIFFS.exists(STATE_FILE)) {
    Serial.println("[STATE] Removing existing file");
    SPIFFS.remove(STATE_FILE);
  }

  File file = SPIFFS.open(STATE_FILE, "w");

  if (!file) {
    Serial.println("[STATE] Failed to create file");
    return;
  } else {
    mergeState(newState);
    Serial.println("[STATE] Saving");
    if (serializeJson(currentState, file) == 0) {
      Serial.println("[STATE] Failed to write file");
    }
    file.close();
  }
}

// Load state from a file
void State::load() {

  if (SPIFFS.exists(STATE_FILE)) {
    Serial.println("[STATE] Loading existing file");

    // Open file for reading
    File file                  = SPIFFS.open(STATE_FILE, "r");
    DeserializationError error = deserializeJson(currentState, file);
    file.close();

    if (error) {
      Serial.println("[STATE] Failed to read file, using default");
      loadDefaultState();
    }

  } else {
    Serial.println("[STATE] File not found, using default");
    loadDefaultState();
  }
}

void State::print(){
     FSInfo info;
     SPIFFS.info(info);
     Serial.printf("[STATE] Total Bytes: %u\r\n",     info.totalBytes);
     Serial.printf("[STATE] Used Bytes: %u\r\n",      info.usedBytes);
     Serial.printf("[STATE] Block Size: %u\r\n",      info.blockSize);
     Serial.printf("[STATE] Page Size: %u\r\n",       info.pageSize);
     Serial.printf("[STATE] Max Open Files: %u\r\n",  info.maxOpenFiles);
     Serial.printf("[STATE] Max Path Length: %u\r\n", info.maxPathLength);

     serializeJsonPretty(currentState, Serial);
     Serial.println("\n");
}

void State::remove(){
  if (SPIFFS.exists(STATE_FILE)) {
    Serial.println("[STATE] Removing file");
    SPIFFS.remove(STATE_FILE);
  }else{
    Serial.println("[STATE] file do not exists");
  }
}
/*
 * updates pin[] values based on currentState
 * Ex:
 *     DEVICE[6] = "DHT":
 *        pin[6] = 4
 *        digitalRead(pin[6]) ~ digitalRead(4)
 *
 *    ACTION[2] = "FAN":
 *         pin[2] = 8
 *         digitalWrite(pin[2], value) ~ digitalWrite(8, value)
 */
void State::getPin(int pin[], const char* DEVICE[], int length){
  JsonObject currentPIN = currentState[NODE::CONFIG][NODE::PIN];
  char buffer [1];
  for(int i = 0 ; i < length ; i++){
    pin[i] = -1;
    for(int j = 0 ; j <= PIN_SIZE ; j++ ){
      if(currentPIN[itoa(j, buffer, 10)] == DEVICE[i]){
        pin[i] = j;
      }
    }
  }
}
