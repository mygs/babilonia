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
char NODE_IP[IP_SIZE];

StaticJsonDocument<JSON_MEMORY_SIZE> inboundData;
StaticJsonDocument<JSON_MEMORY_SIZE> outboundData;
StaticJsonDocument<JSON_MEMORY_SIZE> sensorsTickerData;

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
  outboundData[NODE::NODE_IP] = NODE_IP;
  outboundData[NODE::FIRMWARE_VER] = FIRMWARE_VERSION;

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

      const char* MSG_ID = inboundData[NODE::MESSAGE_ID];

      Serial.printf("\r\n[MQTT] Message arrived ID[%s]\r\n", MSG_ID);
      outboundData[NODE::MESSAGE_ID] = MSG_ID;

      JsonObject config = inboundData[NODE::CONFIG];
      if(!config.isNull()){
        state.save(inboundData);
        command.updatePorts(state);
        status.updatePorts(state);
      }

      JsonObject cmd = inboundData[NODE::COMMAND];
      if(!cmd.isNull()){
        command.execute(state, cmd);
        if (cmd[NODE::RESET].isNull() && cmd[NODE::REBOOT].isNull() ){
          state.save(inboundData);
        }
        //adding executed  command to response!
        outboundData[NODE::COMMAND] = inboundData[NODE::COMMAND];
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

void setupNewWifi() {
  while (Serial.available()) Serial.read(); // flush

  String ssid = "";
  String passwd = "";
  StaticJsonDocument<JSON_MEMORY_SIZE> wifi;

  Serial.println("[SERIAL] Reconfiguring CONNECTION setup ...");
  Serial.print("Enter WiFi SSID: ");
  ssid = Serial.readStringUntil('\n');
  Serial.print("\nEnter WiFi PASSWORD:");
  passwd = Serial.readStringUntil('\n');

  //removing unecessary ending char
  ssid.trim();
  passwd.trim();

  Serial.println("\nWiFi SSID:" + ssid);
  Serial.println("WiFi PASSWORD:" + passwd);

  JsonObject CONFIG = wifi.createNestedObject(NODE::CONFIG);
  CONFIG[NODE::SSID]     = ssid;
  CONFIG[NODE::PASSWORD] = passwd;

  state.save(wifi);

  Serial.println("[SERIAL] Ended CONNECTION setup");
}

void setupWifi() {

  Serial.print("[WIFI] MAC: ");
  Serial.println(WiFi.macAddress());

  Serial.print("[WIFI] Connecting to SSID: ");
  Serial.println(state.getSsid());
  WiFi.mode(WIFI_STA);
  WiFi.begin(state.getSsid(), state.getPassword());

  while (WiFi.waitForConnectResult() != WL_CONNECTED) {
    Serial.printf("[WIFI] Connection Failed! Rebooting in %i seconds...",
                  state.getWifiRetryConnectionDelay() / 1000);
    delay(state.getWifiRetryConnectionDelay());

    serialCommands(); // just in case wifi was badly configured

    ESP.restart();
  }

  IPAddress ip = WiFi.localIP();
  sprintf(NODE_IP, "%d.%d.%d.%d", ip[0],ip[1],ip[2],ip[3]);
  Serial.printf("[WIFI] IP address: %s\n", NODE_IP);
}

/* DO NOT CHANGE this function name - Arduino hook */
void setup() {

  state.load();
  status.updatePorts(state);
  command.updatePorts(state);

  JsonObject cmd = state.getCommand();
  command.execute(state, cmd);

  Serial.begin(state.getSerialBaudRate());
  Serial.setTimeout(3000);
  //while (!Serial) continue;

  state.print();

  sprintf(HOSTNAME, "oasis-%06x", ESP.getChipId());
  Serial.printf("\r\n\r\n[OASIS] Hostname: %s", HOSTNAME);
  Serial.printf("\r\n[OASIS] Firmware version: %s\r\n", FIRMWARE_VERSION);
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

  // For sure, we do not need short heartbeat
  if(state.getHeartBeatPeriod() > THRESHOLD_DISABLE_HEARTBEAT){
    heartBeatTicker.attach_ms(state.getHeartBeatPeriod(), heartBeat);
  }else{
    Serial.println("[OASIS] HeartBeat not enabled");
  }

  Serial.println("[OASIS] Setup Completed");
}

void mqttReconnect() {
  mqtt.disconnect();

  // Loop until we're reconnected
  while (!mqtt.connected()) {
    Serial.print("[MQTT] Attempting connection...");
    if (mqtt.connect(HOSTNAME,MQTT_WILL_TOPIC,MQTT_WILL_QOS,MQTT_WILL_RETAIN,MQTT_WILL_MESSAGE)) {
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
  sprintf(message, "{\"%s\":\"oasis-%06x\"}",NODE::NODE_ID,ESP.getChipId());
  mqtt.publish(state.getMqttHeartBeatTopic(), message);
}

void collectSensorData(){
  sensorsTickerData.clear();
  sensorsTickerData[NODE::NODE_ID] = HOSTNAME;
  sensorsTickerData[NODE::NODE_IP] = NODE_IP;
  sensorsTickerData[NODE::FIRMWARE_VER] = FIRMWARE_VERSION;
  status.collectForSensorTicket(state, sensorsTickerData);
  postResponse(sensorsTickerData);
}

void serialCommands() {
  // only when you receive data:
  if (Serial.available() > 0) {
    // read the incoming byte:
    int incomingByte = Serial.read();
    switch(incomingByte){
      case 27: //ESC
          Serial.println("[SERIAL] Reseting state to initial configuration!");
          state.remove();
          break;
      case 63: //?
          Serial.printf("[SERIAL] Hostname: %s\r\n", HOSTNAME);
          Serial.printf("[SERIAL] Firmware: %s\r\n", FIRMWARE_VERSION);
          Serial.print("[SERIAL] MAC: ");
          Serial.println(WiFi.macAddress());
          Serial.printf("[SERIAL] IP: %s\r\n", NODE_IP);
          break;
      case 99: //c
          {
            setupNewWifi();
          }
          break;
      case 114: //r
          Serial.println("[SERIAL] Rebooting ...");
          ESP.restart();
          break;
      default:
          Serial.print("[SERIAL] Unknown command: ");
          Serial.println(incomingByte, DEC);
    }

  }
}

long previousMillis = millis();

/* DO NOT CHANGE this function name - Arduino hook */
void loop() {
  ArduinoOTA.handle();

  if (!mqtt.connected()) {
    mqttReconnect();
  } else {
    mqtt.loop();
  }
  // DHT and Ticker does not work together, so ...
  unsigned long currentMillis = millis();
  if(currentMillis - previousMillis > state.getSensorCollectDataPeriod()) {
    previousMillis = currentMillis;
    collectSensorData();
  }

  serialCommands();
}
