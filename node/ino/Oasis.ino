#include "Oasis.h"
#include <ESP8266WiFi.h>
#include <ESP8266mDNS.h>
#include <ArduinoOTA.h>
#include <Ticker.h>
#include "WifiSec.h"
#include "PubSubClient.h"
#include "ArduinoJson.h"

char hostname[15];
WiFiClient espClient;
PubSubClient mqtt(espClient);
// Memory pool for JSON object tree.
// Use arduinojson.org/assistant to compute the capacity.
StaticJsonBuffer<200> jsonBuffer;
// StaticJsonBuffer allocates memory on the stack, it can be
// replaced by DynamicJsonBuffer which allocates in the heap.
// DynamicJsonBuffer  jsonBuffer(200);

Ticker sensors;

void onMqttMessage(char* topic, byte* payload, unsigned int length) {
  JsonObject& msg = jsonBuffer.parseObject(payload);
  if (!msg.success()) {
    Serial.println("[MQTT] JSON parsing failed");
    return;
  }

  #ifdef DEBUG_ESP_OASIS
    DEBUG_OASIS("\n[MQTT] Message arrived [");
    DEBUG_OASIS(topic);
    DEBUG_OASIS("] ");
    DEBUG_OASIS(msg.printTo(Serial));
    DEBUG_OASIS("\n");
  #endif
}

void setupWifi() {
  Serial.print("[WIFI] Connecting to SSID: ");
  Serial.println(WifiSec::SSID);
  WiFi.mode(WIFI_STA);
  WiFi.begin( WifiSec::SSID, WifiSec::PASSWORD);
  while (WiFi.waitForConnectResult() != WL_CONNECTED) {
    Serial.println("[WIFI] Connection Failed! Rebooting...");
    delay(5000);
    ESP.restart();
  }
  Serial.print("[WIFI] IP address: ");
  Serial.println(WiFi.localIP());
}

void setup() {
  Serial.begin(115200);
  sprintf(hostname, "oasis-%06x", ESP.getChipId());
  Serial.print("\n\n\n[OASIS] Hostname: ");
  Serial.println(hostname);
  #ifdef DEBUG_ESP_OASIS
    DEBUG_OASIS("[OASIS] Starting Setup\n");
  #endif
  setupWifi();
  ArduinoOTA.setHostname(hostname);
  ArduinoOTA.setPort(OTA_PORT);
  ArduinoOTA.onStart([]() { Serial.println("[OTA] Starting "); });
  ArduinoOTA.onEnd([]() { Serial.println("\n[OTA] Update finished! Rebooting"); });
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
  mqtt.setServer(MQTT_SERVER,MQTT_PORT);
  mqtt.setCallback(onMqttMessage);
  mqttReconnect();
  #ifdef DEBUG_ESP_OASIS
    DEBUG_OASIS("[OASIS] Setup Completed\n");
  #endif

  sensors.attach(180/*segs*/, collectSensorData);
}

void mqttReconnect() {
  mqtt.disconnect();
  // Loop until we're reconnected
  while (!mqtt.connected()) {
    Serial.print("[MQTT] Attempting connection...");
    if (mqtt.connect(hostname)) {
      Serial.println("connected");
      mqtt.subscribe(MQTT_TOPIC_INBOUND);
    } else {
      Serial.print("failed, rc=");
      Serial.print(mqtt.state());
      Serial.println(" try again in 5 seconds");
      delay(5000); // Wait 5 seconds before retrying
    }
  }
}

void collectSensorData(){
  mqtt.publish(MQTT_TOPIC_OUTBOUND, "XYZ", true);

}



void loop() {

  ArduinoOTA.handle();

  if (!mqtt.connected()) {
    mqttReconnect();
  }else{
    mqtt.loop();
  }

}
