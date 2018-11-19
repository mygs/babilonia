#include "Config.h"
#include "WifiSec.h"
#include <ESP8266WiFi.h>
#include <ESP8266mDNS.h>
#include <ArduinoOTA.h>
#include "PubSubClient.h"
#include "ArduinoJson.h"


char hostname[15];
WiFiClient espClient;
PubSubClient mqtt_client(espClient);
// Memory pool for JSON object tree.
// Use arduinojson.org/assistant to compute the capacity.
StaticJsonBuffer<200> jsonBuffer;
// StaticJsonBuffer allocates memory on the stack, it can be
// replaced by DynamicJsonBuffer which allocates in the heap.
// DynamicJsonBuffer  jsonBuffer(200);

void callback(char* topic, byte* payload, unsigned int length) {
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

void setup_wifi() {
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
  setup_wifi();
  ArduinoOTA.setHostname(hostname);
  ArduinoOTA.setPort(Config::OTA_PORT);
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
  mqtt_client.setServer(Config::MQTT_SERVER, Config::MQTT_PORT);
  mqtt_client.setCallback(callback);
  #ifdef DEBUG_ESP_OASIS
    DEBUG_OASIS("[OASIS] Setup Completed\n");
  #endif
}

void mqtt_reconnect() {
  #ifdef DEBUG_ESP_OASIS
    DEBUG_OASIS("[WiFi] status:");
    DEBUG_OASIS(WiFi.status());
    DEBUG_OASIS("\n");
  #endif
  // Loop until we're reconnected
  while (!mqtt_client.connected()) {
    Serial.print("[MQTT] Attempting connection...");
    if (mqtt_client.connect(hostname)) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(mqtt_client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}


void loop() {

  ArduinoOTA.handle();

  if (!mqtt_client.connected()) {
    mqtt_reconnect();
  }
  mqtt_client.loop();
  //mqtt_client.publish("/arduino", "XYZ", true);
  mqtt_client.subscribe("/commands");

}
