#include <State.h>
#include <InitialConfiguration.h>
#include <FS.h> // Include the SPIFFS library


State::State(){
  if (!SPIFFS.begin()) {
      Serial.println("Failed to mount file system");
  }
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
void State::mergeState(JsonDocument& base, JsonDocument& arrived) {

  JsonObject arrivedConfig = arrived["CONFIG"];

  if(!arrivedConfig.isNull()){
    JsonObject baseConfig = base["CONFIG"];

    baseConfig["SSID"]        = diffs(baseConfig["SSID"], arrivedConfig["SSID"]);
    baseConfig["PASSWORD"]    = diffs(baseConfig["PASSWORD"], arrivedConfig["PASSWORD"]);
    baseConfig["MQTT_SERVER"] = diffs(baseConfig["MQTT_SERVER"], arrivedConfig["MQTT_SERVER"]);
    baseConfig["MQTT_PORT"]   = diffi(baseConfig["MQTT_PORT"],
                                arrivedConfig["MQTT_PORT"]);
    baseConfig["MQTT_TOPIC_INBOUND"] =
      diffs(baseConfig["MQTT_TOPIC_INBOUND"],  arrivedConfig["MQTT_TOPIC_INBOUND"]);
    baseConfig["MQTT_TOPIC_OUTBOUND"] =
      diffs(baseConfig["MQTT_TOPIC_OUTBOUND"], arrivedConfig["MQTT_TOPIC_OUTBOUND"]);
    baseConfig["PERIOD"] = diffi(base["PERIOD"], arrivedConfig["PERIOD"]);

    JsonObject arrivedPIN = arrivedConfig["PIN"];
    if(!arrivedPIN.isNull()){
      JsonObject basePIN    = baseConfig["PIN"];

      basePIN["0"] = diffs(basePIN["0"], arrivedPIN["0"]);
      basePIN["1"] = diffs(basePIN["1"], arrivedPIN["1"]);
      basePIN["2"] = diffs(basePIN["2"], arrivedPIN["2"]);
      basePIN["3"] = diffs(basePIN["3"], arrivedPIN["3"]);
      basePIN["4"] = diffs(basePIN["4"], arrivedPIN["4"]);
      basePIN["5"] = diffs(basePIN["5"], arrivedPIN["5"]);
      basePIN["6"] = diffs(basePIN["6"], arrivedPIN["6"]);
      basePIN["7"] = diffs(basePIN["7"], arrivedPIN["7"]);
      basePIN["8"] = diffs(basePIN["8"], arrivedPIN["8"]);
    }
  }

  JsonObject arrivedCommand = arrived["COMMAND"];
  if(!arrivedCommand.isNull()){
    JsonObject baseCommand = base["COMMAND"];

    baseCommand["LIGHT"] = diffb(baseCommand["LIGHT"], arrivedCommand["LIGHT"]);
    baseCommand["FAN"] = diffb(baseCommand["FAN"], arrivedCommand["FAN"]);
    baseCommand["WATER"] = diffb(baseCommand["WATER"], arrivedCommand["WATER"]);
  }
}
void State::loadDefaultState(JsonDocument& state){
  state.clear();
  JsonObject CONFIG = state.createNestedObject("CONFIG");
  CONFIG["SSID"]                = InitialConfiguration::SSID;
  CONFIG["PASSWORD"]            = InitialConfiguration::PASSWORD;
  CONFIG["MQTT_SERVER"]         = InitialConfiguration::MQTT_SERVER;
  CONFIG["MQTT_PORT"]           = InitialConfiguration::MQTT_PORT;
  CONFIG["MQTT_TOPIC_INBOUND"]  = InitialConfiguration::MQTT_TOPIC_INBOUND;
  CONFIG["MQTT_TOPIC_OUTBOUND"] = InitialConfiguration::MQTT_TOPIC_OUTBOUND;
  CONFIG["PERIOD"]              = InitialConfiguration::PERIOD;
  JsonObject PIN = CONFIG.createNestedObject("PIN");
  PIN["0"] = InitialConfiguration::PIN0;
  PIN["1"] = InitialConfiguration::PIN1;
  PIN["2"] = InitialConfiguration::PIN2;
  PIN["3"] = InitialConfiguration::PIN3;
  PIN["4"] = InitialConfiguration::PIN4;
  PIN["5"] = InitialConfiguration::PIN5;
  PIN["6"] = InitialConfiguration::PIN6;
  PIN["7"] = InitialConfiguration::PIN7;
  PIN["8"] = InitialConfiguration::PIN8;

  JsonObject COMMAND = state.createNestedObject("COMMAND");
  COMMAND["LIGHT"] = false;
  COMMAND["FAN"] = false;
  COMMAND["WATER"] = false;

  Serial.println("[STATE] creating default file");
  saveDefaultState(state);

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
void State::saveState(JsonDocument& currentState, JsonDocument& newState) {
  if (SPIFFS.exists(STATE_FILE)) {
    Serial.println("[STATE] Removing existing file");
    SPIFFS.remove(STATE_FILE);
  }

  File file = SPIFFS.open(STATE_FILE, "w");

  if (!file) {
    Serial.println("[STATE] Failed to create file");
    return;
  } else {
    mergeState(currentState, newState);
    Serial.println("[STATE] Saving");
    if (serializeJson(currentState, file) == 0) {
      Serial.println("[STATE] Failed to write file");
    }
    file.close();
  }
}

// Load state from a file
void State::loadState(JsonDocument& state) {

  if (SPIFFS.exists(STATE_FILE)) {
    Serial.println("[STATE] Loading existing file");

    // Open file for reading
    File file                  = SPIFFS.open(STATE_FILE, "r");
    DeserializationError error = deserializeJson(state, file);
    file.close();

    if (error) {
      Serial.println("[STATE] Failed to read file, using default");
      loadDefaultState(state);
    }

  } else {
    Serial.println("[STATE] File not found, using default");
    loadDefaultState(state);
  }

  #ifdef DEBUG_ESP_OASIS
  serializeJsonPretty(state, Serial);
  Serial.println("\n");
  #endif // ifdef DEBUG_ESP_OASIS
}

void State::printFileSystemDetails(){
     FSInfo info;
     SPIFFS.info(info);
     Serial.printf("[STATE] Total Bytes: %u\r\n",     info.totalBytes);
     Serial.printf("[STATE] Used Bytes: %u\r\n",      info.usedBytes);
     Serial.printf("[STATE] Block Size: %u\r\n",      info.blockSize);
     Serial.printf("[STATE] Page Size: %u\r\n",       info.pageSize);
     Serial.printf("[STATE] Max Open Files: %u\r\n",  info.maxOpenFiles);
     Serial.printf("[STATE] Max Path Length: %u\r\n", info.maxPathLength);
}
