#include <ArduinoJson.h>
#include <ESP8266WiFi.h>
#include <ESP8266mDNS.h>
#include <ArduinoOTA.h>
#include <Ticker.h>
#include <PubSubClient.h>
#include "Oasis.h"
#include "State.h"
#include "Status.h"
#include "Command.h"
#include "OasisConstants.h"

WiFiClient   wifiClient;
PubSubClient mqtt(wifiClient);
char payload[JSON_MEMORY_SIZE];
char HOSTNAME[HOSTNAME_SIZE];

StaticJsonDocument<JSON_MEMORY_SIZE> inboundData;
StaticJsonDocument<JSON_MEMORY_SIZE> outboundData;
StaticJsonDocument<JSON_MEMORY_SIZE> sensorsTickerData;

Ticker sensorsTicker;
Ticker heartBeatTicker;

State state;
Status status;
Command command;

void postResponse(const JsonDocument& message) {
  // Produce a minified JSON document
  int plength = measureJson(message);
  serializeJson(message, payload, JSON_MEMORY_SIZE);
  mqtt.publish(state.getMqttOutboundTopic(), payload, plength);
}

void onMqttMessage(char *topic, byte *payload, unsigned int length) {
  outboundData.clear();
  outboundData[NODE::NODE_ID] = HOSTNAME;
  DeserializationError error = deserializeJson(inboundData, (char *)payload, length);
  if (error) {
    char error_message[64];
    sprintf(error_message, "JSON deserialize failed with code %s",error.c_str());
    outboundData[NODE::ERROR] = error_message;
    Serial.println(error_message);
    postResponse(outboundData);
    inboundData.clear();
  } else {
    if( strcmp(NODE::ALL, inboundData[NODE::NODE_ID]) == 0 ||
        strcmp(HOSTNAME , inboundData[NODE::NODE_ID]) == 0){
      outboundData[NODE::MESSAGE_ID] = inboundData[NODE::MESSAGE_ID];
      Serial.print("\n[MQTT] Message arrived ID[");
      const char* MSG_ID = inboundData[NODE::MESSAGE_ID];
      Serial.print(MSG_ID);
      Serial.println("]");

      JsonObject config = inboundData[NODE::CONFIG];
      if(!config.isNull()){
        state.save(inboundData);
      }

      JsonObject cmd = inboundData[NODE::COMMAND];
      if(!cmd.isNull()){
        command.execute(state, cmd);
        if (cmd[NODE::RESET].isNull()){
          state.save(inboundData);
        }
      }

      JsonArray stat = inboundData[NODE::STATUS];
      if(!stat.isNull()){
        status.collect(state, stat, outboundData);
      }
      postResponse(outboundData);
      inboundData.clear();
    }
  }
}

void setupWifi() {
  Serial.print("[WIFI] Connecting to SSID: ");
  Serial.println(state.getSsid());
  WiFi.mode(WIFI_STA);
  WiFi.begin(state.getSsid(), state.getPassword());

  while (WiFi.waitForConnectResult() != WL_CONNECTED) {
    Serial.printf("[WIFI] Connection Failed! Rebooting in %i seconds...",
                  state.getWifiRetryConnectionDelay() / 1000);
    delay(state.getWifiRetryConnectionDelay());
    ESP.restart();
  }
  Serial.print("[WIFI] IP address: ");
  Serial.println(WiFi.localIP());
}

/* DO NOT CHANGE this function name - Arduino hook */
void setup() {

  state.load();

  Serial.begin(state.getSerialBaudRate());

  //while (!Serial) continue;

  state.print();

  sprintf(HOSTNAME, "oasis-%06x", ESP.getChipId());
  Serial.print("\n\n\n[OASIS] Hostname: ");
  Serial.println(HOSTNAME);
  Serial.println("[OASIS] Starting Setup");

  setupWifi();

  ArduinoOTA.setHostname(HOSTNAME);
  ArduinoOTA.setPort(state.getOtaPort());
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

  heartBeat(); // Oasis is up and running, notify it
  heartBeatTicker.attach(state.getHeartBeatPeriod(), heartBeat);

  sensorsTicker.attach(state.getSensorCollectDataPeriod(), collectSensorData);
  Serial.println("[OASIS] Setup Completed");
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
      Serial.printf(" try again in %i seconds", state.getWifiRetryConnectionDelay() / 1000);
      delay(state.getWifiRetryConnectionDelay());
    }
  }
}

void heartBeat() {
  char message[HEARTBEAT_MESSAGE_SIZE];
  sprintf(message, "{\"%s\": \"oasis-%06x\"}",NODE::NODE_ID,ESP.getChipId());
  mqtt.publish(state.getMqttOutboundTopic(), message);
}

void collectSensorData(){
  sensorsTickerData.clear();
  sensorsTickerData[NODE::NODE_ID] = HOSTNAME;
  status.collectForSensorTicket(state, sensorsTickerData);
  postResponse(sensorsTickerData);
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
