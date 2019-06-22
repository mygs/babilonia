#include <ArduinoJson.h>
#include <ESP8266WiFi.h>
#include <ESP8266mDNS.h>
#include <ArduinoOTA.h>
#include <Ticker.h>
#include <PubSubClient.h>
#include "Oasis.h"
#include "State.h"
#include "Command.h"

WiFiClient   wifiClient;
PubSubClient mqtt(wifiClient);
char payload[JSON_MEMORY_SIZE];
char HOSTNAME[HOSTNAME_SIZE];

StaticJsonDocument<JSON_MEMORY_SIZE> data;

Ticker sensors;
State state;
Command command;

void postResponse() {
  data.clear();
  data["node"] = HOSTNAME;
  JsonArray resp = data.createNestedArray("resp");
  resp.add("cfg");

  // Produce a minified JSON document
  int plength = measureJson(data);
  serializeJson(data, payload, JSON_MEMORY_SIZE);
  mqtt.publish(state.getMqttOutboundTopic(), payload, plength);
}

void onMqttMessage(char *topic, byte *payload, unsigned int length) {
  DeserializationError error = deserializeJson(data, (char *)payload, length);

  if (error) {
    #ifdef DEBUG_ESP_OASIS
    Serial.print("\n\n[JSON] Deserialize failed with code ");
    Serial.println(error.c_str());
    #endif // ifdef DEBUG_ESP_OASIS
  } else {
    #ifdef DEBUG_ESP_OASIS
    Serial.print("\n[MQTT] Message arrived ID[");
    const char* ID = data["ID"];
    Serial.print(ID);
    Serial.println("]");
    JsonObject CONFIG = data["CONFIG"];
    JsonObject COMMAND = data["COMMAND"];
    if(!CONFIG.isNull() || !COMMAND.isNull()){
      state.saveState(data);
      //command.execute(STATE, COMMAND);
    }
    JsonArray STATUS = data["STATUS"];
    if(!STATUS.isNull()){
      Serial.println("TEM STATUS");

    }
    //serializeJsonPretty(data, Serial);
    #endif // ifdef DEBUG_ESP_OASIS
    postResponse();
  }
}

void setupWifi() {
  Serial.print("[WIFI] Connecting to SSID: ");
  Serial.println(state.getSsid());
  WiFi.mode(WIFI_STA);
  WiFi.begin(state.getSsid(), state.getPassword());

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

  state.loadState();

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
  mqtt.setServer(state.getMqttServer(),
                 state.getMqttPort());
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
      mqtt.subscribe(state.getMqttInboundTopic());
    } else {
      Serial.print("failed, rc=");
      Serial.print(mqtt.state());
      Serial.printf(" try again in %i seconds", RETRY_CONNECTION_DELAY / 1000);
      delay(RETRY_CONNECTION_DELAY);
    }
  }
}

void collectSensorData() {
  mqtt.publish(state.getMqttOutboundTopic(), "XYZW");
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
