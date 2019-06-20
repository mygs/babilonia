#include <InitialConfiguration.h>
#include <ArduinoJson.h>
#include <ESP8266WiFi.h>
#include <ESP8266mDNS.h>
#include <ArduinoOTA.h>
#include <Ticker.h>
#include <PubSubClient.h>
#include <FS.h> // Include the SPIFFS library
#include <Oasis.h>

WiFiClient   wifiClient;
PubSubClient mqtt(wifiClient);
char payload[JSON_MEMORY_SIZE];
char HOSTNAME[HOSTNAME_SIZE];
StaticJsonDocument<JSON_MEMORY_SIZE> STATE;

// Memory pool for JSON object tree.
// Because it doesn’t call malloc() and free(),
// StaticJsonDocument is slightly faster than DynamicJsonDocument
StaticJsonDocument<JSON_MEMORY_SIZE> jsonDoc;

Ticker sensors;

// Save State to a file
void saveState(JsonDocument& _state) {

  Serial.println("[STATE] Saving");

  if (!SPIFFS.exists(STATE_FILE)) {
    Serial.println("[STATE] Removing existing file");

    SPIFFS.remove(STATE_FILE);
  }
  File file = SPIFFS.open(STATE_FILE, "w");

  if (!file) {
    Serial.println("[STATE] Failed to create file");
    return;
  } else {
    // Serialize JSON to file
    mergeState(STATE, _state);
    Serial.println("[STATE] Merged");

    if (serializeJsonPretty(STATE, file) == 0) {
      Serial.println("[STATE] Failed to write file");
    }
    file.close();
  }
}

const char* diffs(JsonVariant _base, JsonVariant _arrived) {
  const char *arrived = _arrived.as<char *>();
  if ((arrived != NULL) && (arrived[0] != '\0')) {
    return arrived;
  } else {
    return _base.as<char *>();
  }
}

int diffi(JsonVariant _base, JsonVariant _arrived) {
  int arrived = _arrived.as<int>();
  if (arrived >= 0) {
    return arrived;
  } else {
    return _base.as<int>();
  }
}

bool diffb(JsonVariant _base, JsonVariant _arrived) {
  if (!_arrived.isNull()) {
    return _arrived.as<bool>();
  } else {
    return _base.as<bool>();
  }
}

// Merge state
void mergeState(JsonDocument& base, JsonDocument& arrived) {

  JsonObject baseConfig = base["CONFIG"];
  JsonObject arrivedConfig = arrived["CONFIG"];

  if(!arrivedConfig.isNull()){
    #ifdef DEBUG_ESP_OASIS
    Serial.println("[STATE] Merging CONFIG");
    #endif // ifdef DEBUG_ESP_OASIS
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
    JsonObject basePIN    = baseConfig["PIN"];
    JsonObject arrivedPIN = arrivedConfig["PIN"];
    if(!arrivedPIN.isNull()){
      #ifdef DEBUG_ESP_OASIS
      Serial.println("[STATE] Merging PIN");
      #endif // ifdef DEBUG_ESP_OASIS
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
  JsonObject baseCommand = base["COMMAND"];
  if(!arrivedCommand.isNull()){
    #ifdef DEBUG_ESP_OASIS
    Serial.println("[STATE] Merging COMMAND");
    #endif // ifdef DEBUG_ESP_OASIS
    baseCommand["LIGHT"] = diffb(baseCommand["LIGHT"], arrivedCommand["LIGHT"]);
    baseCommand["FAN"] = diffb(baseCommand["FAN"], arrivedCommand["FAN"]);
    baseCommand["WATER"] = diffb(baseCommand["WATER"], arrivedCommand["WATER"]);

  }
}

// Load state from a file
void loadState() {
  Serial.println("[STATE] Loading");

  if (SPIFFS.exists(STATE_FILE)) {
    Serial.println("[STATE] Loading existing file");

    // Open file for reading
    File file                  = SPIFFS.open(STATE_FILE, "r");
    DeserializationError error = deserializeJson(STATE, file);
    file.close();

    if (error) {
      #ifdef DEBUG_ESP_OASIS
      Serial.println(
        "\n\n[STATE] Failed to read file, using default");
        loadDefaultState();
        Serial.println("[STATE] creating default file");
        saveState(STATE);
      #endif // ifdef DEBUG_ESP_OASIS
    }

  } else {
    Serial.println("[STATE] File not found, using default");
    loadDefaultState();
    Serial.println("[STATE] creating default file");
    saveState(STATE);
  }

  #ifdef DEBUG_ESP_OASIS
  serializeJsonPretty(STATE, Serial);
  Serial.println("\n");
  #endif // ifdef DEBUG_ESP_OASIS
}

void loadDefaultState(){
  JsonObject CONFIG = STATE.createNestedObject("CONFIG");
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

  JsonObject COMMAND = STATE.createNestedObject("COMMAND");
  COMMAND["LIGHT"] = false;
  COMMAND["FAN"] = false;
  COMMAND["WATER"] = false;
}

void postResponse() {
  jsonDoc.clear();
  jsonDoc["node"] = HOSTNAME;
  JsonArray resp = jsonDoc.createNestedArray("resp");
  resp.add("cfg");

  // Produce a minified JSON document
  int plength = measureJson(jsonDoc);
  serializeJson(jsonDoc, payload, JSON_MEMORY_SIZE);
  mqtt.publish(STATE["MQTT_TOPIC_OUTBOUND"], payload, plength);
}

void onMqttMessage(char *topic, byte *payload, unsigned int length) {
  DeserializationError error = deserializeJson(jsonDoc, (char *)payload, length);

  if (error) {
    #ifdef DEBUG_ESP_OASIS
    Serial.print("\n\n[JSON] Deserialize failed with code ");
    Serial.println(error.c_str());
    #endif // ifdef DEBUG_ESP_OASIS
  } else {
    #ifdef DEBUG_ESP_OASIS
    Serial.print("\n[MQTT] Message arrived ID[");
    const char* ID = jsonDoc["ID"];
    Serial.print(ID);
    Serial.println("]");
    JsonObject CONFIG = jsonDoc["CONFIG"];
    JsonObject COMMAND = jsonDoc["COMMAND"];
    if(!CONFIG.isNull() || !COMMAND.isNull()){
      //saveState(jsonDoc);
      saveState(STATE);
    }
    JsonArray STATUS = jsonDoc["STATUS"];
    if(!STATUS.isNull()){
      Serial.println("TEM STATUS");

    }
    //serializeJsonPretty(jsonDoc, Serial);
    #endif // ifdef DEBUG_ESP_OASIS
    postResponse();
  }
}

void setupWifi() {
  Serial.print("[WIFI] Connecting to SSID: ");
  Serial.println(STATE["CONFIG"]["SSID"].as<char *>());
  WiFi.mode(WIFI_STA);
  WiFi.begin(STATE["CONFIG"]["SSID"].as<char *>(), STATE["CONFIG"]["PASSWORD"].as<char *>());

  while (WiFi.waitForConnectResult() != WL_CONNECTED) {
    Serial.printf("[WIFI] Connection Failed! Rebooting in %i seconds...",
                  RETRY_CONNECTION_DELAY / 1000);
    delay(RETRY_CONNECTION_DELAY);
    ESP.restart();
  }
  Serial.print("[WIFI] IP address: ");
  Serial.println(WiFi.localIP());
}

/* DO NOT CHANGE this function name - Arduino hook */
void setup() {
  Serial.begin(SERIAL_BAUDRATE);

  while (!Serial) continue;
  sprintf(HOSTNAME, "oasis-%06x", ESP.getChipId());
  Serial.print("\n\n\n[OASIS] Hostname: ");
  Serial.println(HOSTNAME);
 #ifdef DEBUG_ESP_OASIS
  Serial.println("[OASIS] Starting Setup");
 #endif // ifdef DEBUG_ESP_OASIS

  if (!SPIFFS.begin()) {
    Serial.println("Failed to mount file system");
  }

 #ifdef DEBUG_ESP_OASIS
  FSInfo info;
  SPIFFS.info(info);
  Serial.printf("Total Bytes: %u\r\n",     info.totalBytes);
  Serial.printf("Used Bytes: %u\r\n",      info.usedBytes);
  Serial.printf("Block Size: %u\r\n",      info.blockSize);
  Serial.printf("Page Size: %u\r\n",       info.pageSize);
  Serial.printf("Max Open Files: %u\r\n",  info.maxOpenFiles);
  Serial.printf("Max Path Length: %u\r\n", info.maxPathLength);
 #endif // ifdef DEBUG_ESP_OASIS

 //TODO: REMOVEME
  //SPIFFS.remove(STATE_FILE);

  loadState();
  setupWifi();
  ArduinoOTA.setHostname(HOSTNAME);
  ArduinoOTA.setPort(OTA_PORT);
  ArduinoOTA.onStart([]() {
    Serial.println("[OTA] Starting ");
  });
  ArduinoOTA.onEnd([]() {
    Serial.println("\n[OTA] Update finished! Rebooting");
  });
  ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
    Serial.printf("[OTA] Progress: %u%%\r", (progress / (total / 100)));
  });
  ArduinoOTA.onError([](ota_error_t error) {
    Serial.printf("[OTA] Error[%u]: ", error);

    if (error == OTA_AUTH_ERROR) {
      Serial.println("[OTA] Auth Failed");
    } else if (error == OTA_BEGIN_ERROR) {
      Serial.println("[OTA] Begin Failed");
    } else if (error == OTA_CONNECT_ERROR) {
      Serial.println("[OTA] Connect Failed");
    } else if (error == OTA_RECEIVE_ERROR) {
      Serial.println("[OTA] Receive Failed");
    } else if (error == OTA_END_ERROR) {
      Serial.println("[OTA] End Failed");
    }
  });
  ArduinoOTA.begin();
  mqtt.setServer(STATE["CONFIG"]["MQTT_SERVER"].as<char *>(),
                 STATE["CONFIG"]["MQTT_PORT"].as<int>());
  mqtt.setCallback(onMqttMessage);
  mqttReconnect();
 #ifdef DEBUG_ESP_OASIS
  Serial.println("[OASIS] Setup Completed");
 #endif // ifdef DEBUG_ESP_OASIS

  sensors.attach(SENSOR_COLLECT_DATA_PERIOD, collectSensorData);
}

void mqttReconnect() {
  mqtt.disconnect();

  // Loop until we're reconnected
  while (!mqtt.connected()) {
    Serial.print("[MQTT] Attempting connection...");

    if (mqtt.connect(HOSTNAME)) {
      Serial.println("connected");
      mqtt.subscribe(STATE["CONFIG"]["MQTT_TOPIC_INBOUND"]);
    } else {
      Serial.print("failed, rc=");
      Serial.print(mqtt.state());
      Serial.printf(" try again in %i seconds", RETRY_CONNECTION_DELAY / 1000);
      delay(RETRY_CONNECTION_DELAY);
    }
  }
}

void collectSensorData() {
  mqtt.publish(STATE["CONFIG"]["MQTT_TOPIC_OUTBOUND"], "XYZW");
}

/* DO NOT CHANGE this function name - Arduino hook */
void loop() {
  ArduinoOTA.handle();

  if (!mqtt.connected()) {
    mqttReconnect();
  } else {
    mqtt.loop();
  }
}
