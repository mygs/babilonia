#include "Oasis.h"
#include <ESP8266WiFi.h>
#include <ESP8266mDNS.h>
#include <ArduinoOTA.h>
#include <Ticker.h>
#include "WifiSec.h"
#include "PubSubClient.h"
#include "ArduinoJson.h"

char hostname[HOSTNAME_SIZE];
WiFiClient espClient;
PubSubClient mqtt(espClient);
// Memory pool for JSON object tree.
// Use arduinojson.org/assistant to compute the capacity.
StaticJsonDocument<JSON_MEMORY_SIZE> jsonDoc;
StaticJsonDocument<JSON_MEMORY_SIZE> jsonDocOut;

Ticker sensors;

void postResponse(){

        jsonDocOut["node"] = hostname;
        JsonArray resp = jsonDocOut.createNestedArray("resp");
        resp.add("cfg");
        char messageBuffer[64];
        serializeJson(jsonDocOut, messageBuffer, sizeof(messageBuffer));

        mqtt.publish(MQTT_TOPIC_OUTBOUND, messageBuffer);

}


void onMqttMessage(char* topic, byte* payload, unsigned int length) {
        // handle message arrived
        char inData[80];


        Serial.print("payload: ");
        for(int i =0; i<length; i++) {
                Serial.print((char)payload[i]);
                inData[i] = (char)payload[i];
        }
        Serial.println();
        DeserializationError error = deserializeJson(jsonDoc, inData);

        if (error) {
                Serial.print(F("deserializeJson() failed with code "));
                Serial.println(error.c_str());
        }

        postResponse();

  #ifdef DEBUG_ESP_OASIS
        Serial.print("\n[MQTT] Message arrived [");
        Serial.print(topic);
        Serial.print("] ");
        Serial.println(msg.prettyPrintTo(Serial));
  #endif
}

void setupWifi() {
        Serial.print("[WIFI] Connecting to SSID: ");
        Serial.println(WifiSec::SSID);
        WiFi.mode(WIFI_STA);
        WiFi.begin( WifiSec::SSID, WifiSec::PASSWORD);
        while (WiFi.waitForConnectResult() != WL_CONNECTED) {
                Serial.printf("[WIFI] Connection Failed! Rebooting in %i seconds...", RETRY_CONNECTION_DELAY/1000);
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
        sprintf(hostname, "oasis-%06x", ESP.getChipId());
        Serial.print("\n\n\n[OASIS] Hostname: ");
        Serial.println(hostname);
  #ifdef DEBUG_ESP_OASIS
        Serial.println("[OASIS] Starting Setup");
  #endif
        setupWifi();
        ArduinoOTA.setHostname(hostname);
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
        mqtt.setServer(MQTT_SERVER,MQTT_PORT);
        mqtt.setCallback(onMqttMessage);
        mqttReconnect();
  #ifdef DEBUG_ESP_OASIS
        Serial.println("[OASIS] Setup Completed");
  #endif

        sensors.attach(SENSOR_COLLECT_DATA_PERIOD, collectSensorData);
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
                        Serial.printf(" try again in %i seconds", RETRY_CONNECTION_DELAY/1000);
                        delay(RETRY_CONNECTION_DELAY);
                }
        }
}

void collectSensorData(){
        mqtt.publish(MQTT_TOPIC_OUTBOUND, "XYZW");
}


/* DO NOT CHANGE this function name - Arduino hook */
void loop() {

        ArduinoOTA.handle();

        if (!mqtt.connected()) {
                mqttReconnect();
        }else{
                mqtt.loop();
        }

}
