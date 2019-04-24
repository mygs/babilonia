#include <IniCfg.h>
#include <Configuration.h>
#include <Oasis.h>
#include <ESP8266WiFi.h>
#include <ESP8266mDNS.h>
#include <ArduinoOTA.h>
#include <Ticker.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <SD.h>
#include <SPI.h>

WiFiClient   wifiClient;
PubSubClient mqtt(wifiClient);
char payload[JSON_MEMORY_SIZE];
char HOSTNAME[HOSTNAME_SIZE];
// ***** CONFIGURATION *****
StaticJsonDocument<512> config;


// Memory pool for JSON object tree.
// Because it doesn’t call malloc() and free(),
// StaticJsonDocument is slightly faster than DynamicJsonDocument
StaticJsonDocument<JSON_MEMORY_SIZE> jsonDoc;

Ticker sensors;

// Loads the configuration from a file
void loadConfiguration() {
  Serial.println("[CONFIG] Loading configuration ");

  if (SD.exists(CONFIG_FILE)){
    Serial.println("[CONFIG] Loading existing file configuration");
    // Open file for reading
    File file = SD.open(CONFIG_FILE);
    DeserializationError error = deserializeJson(config, file);
    if (error) {
      #ifdef DEBUG_ESP_OASIS
      Serial.println("\n\n[CONFIG] Failed to read file, using default configuration");
      #endif // ifdef DEBUG_ESP_OASIS
    } else {
      #ifdef DEBUG_ESP_OASIS
      serializeJsonPretty(config, Serial);
      #endif // ifdef DEBUG_ESP_OASIS
    }
    file.close();
  }else{
    File file = SD.open(CONFIG_FILE);
    Serial.println("[CONFIG] File not found, using default configuration");
    config["SSID"] = IniCfg::SSID;
    config["PASSWORD"] = IniCfg::PASSWORD;
    config["MQTT_SERVER"] = IniCfg::MQTT_SERVER;
    config["MQTT_PORT"] = IniCfg::MQTT_PORT;
    config["MQTT_TOPIC_INBOUND"] = IniCfg::MQTT_TOPIC_INBOUND;
    config["MQTT_TOPIC_OUTBOUND"] = IniCfg::MQTT_TOPIC_OUTBOUND;
    serializeJsonPretty(config, file);
    file.close();
  }

  //
  // // Parse the root object
  // JsonObject &root = jsonBuffer.parseObject(file);
  //
  // if (!root.success())
  //   Serial.println(F("Failed to read file, using default configuration"));
  //
  // // Copy values from the JsonObject to the Config
  // config.port = root["port"] | 2731;
  // strlcpy(config.hostname,                   // <- destination
  //         root["hostname"] | "example.com",  // <- source
  //         sizeof(config.hostname));          // <- destination's capacity
  //
  // // Close the file (File's destructor doesn't close the file)
  // file.close();
}




void postResponse() {
  jsonDoc.clear();
  jsonDoc["node"] = HOSTNAME;
  JsonArray resp = jsonDoc.createNestedArray("resp");
  resp.add("cfg");

  // Produce a minified JSON document
  int plength = measureJson(jsonDoc);
  serializeJson(jsonDoc, payload, JSON_MEMORY_SIZE);
  mqtt.publish(config["MQTT_TOPIC_OUTBOUND"], payload, plength);
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
    Serial.print("\n[MQTT] Message arrived [");
    Serial.print(topic);
    Serial.println("]");
    serializeJsonPretty(jsonDoc, Serial);
    #endif // ifdef DEBUG_ESP_OASIS
    postResponse();
  }
}

void setupWifi() {
  Serial.print("[WIFI] Connecting to SSID: ");
  Serial.println(config["SSID"]);
  WiFi.mode(WIFI_STA);
  WiFi.begin(config["SSID"], config["PASSWORD"]);

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
 loadConfiguration();
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
  mqtt.setServer(config["MQTT_SERVER"], config["MQTT_PORT"]);
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
      mqtt.subscribe(config["MQTT_TOPIC_INBOUND"]);
    } else {
      Serial.print("failed, rc=");
      Serial.print(mqtt.state());
      Serial.printf(" try again in %i seconds", RETRY_CONNECTION_DELAY / 1000);
      delay(RETRY_CONNECTION_DELAY);
    }
  }
}

void collectSensorData() {
  mqtt.publish(config["MQTT_TOPIC_OUTBOUND"], "XYZW");
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
