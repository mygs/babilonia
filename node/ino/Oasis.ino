#include <ESP8266WiFi.h>
#include "PubSubClient.h"
#include <ESP8266mDNS.h>
#include <sstream>
#include <WiFiUdp.h>
#include <ArduinoOTA.h>
#include "Profile.h"

char HOSTNAME[8];
WiFiClient espClient;
PubSubClient mqtt_client(espClient);

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("[MQTT] Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();
}

void setup_wifi() {
  Serial.print("[WIFI] Connecting to SSID: ");
  Serial.println(Profile::WIFI_SSID);
  WiFi.mode(WIFI_STA);
  WiFi.begin( Profile::WIFI_SSID, Profile::WIFI_PASSWORD);
  while (WiFi.waitForConnectResult() != WL_CONNECTED) {
    Serial.println("[WIFI] Connection Failed! Rebooting...");
    delay(5000);
    ESP.restart();
  }
  Serial.print("[WIFI] IP address: ");
  Serial.println(WiFi.localIP());
}

void setup() {
  sprintf( HOSTNAME, "%lu", ESP.getChipId() );
  Serial.begin(115200);
  Serial.print("\n\n\n[OASIS] HOSTNAME: ");
  Serial.println(HOSTNAME);
  Serial.println("[OASIS] Starting Setup");
  setup_wifi();
  ArduinoOTA.setPort(Profile::PORT);
  ArduinoOTA.setHostname(HOSTNAME);
  ArduinoOTA.onStart([]() { Serial.println("[OTA] Starting "); });
  ArduinoOTA.onEnd([]() { Serial.println("\n[OTA] Update finished! Rebooting"); });
  ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
    Serial.printf("[OTA] Progress: %u%%\r", (progress / (total / 100)));
  });
  ArduinoOTA.onError([](ota_error_t error) {
    Serial.printf("Error[%u]: ", error);
    if (error == OTA_AUTH_ERROR) {
      Serial.println("Auth Failed");
    } else if (error == OTA_BEGIN_ERROR) {
      Serial.println("Begin Failed");
    } else if (error == OTA_CONNECT_ERROR) {
      Serial.println("Connect Failed");
    } else if (error == OTA_RECEIVE_ERROR) {
      Serial.println("Receive Failed");
    } else if (error == OTA_END_ERROR) {
      Serial.println("End Failed");
    }
  });
  ArduinoOTA.begin();
  mqtt_client.setServer(Profile::MQTT_SERVER, Profile::MQTT_PORT);
  mqtt_client.setCallback(callback);
  Serial.println("[OASIS] Setup Completed");
}

void mqtt_reconnect() {
  // Loop until we're reconnected
  while (!mqtt_client.connected()) {
    Serial.print("[MQTT] Attempting connection...");
    if (mqtt_client.connect(HOSTNAME)) {
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
