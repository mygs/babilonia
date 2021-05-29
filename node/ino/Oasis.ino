#include <ArduinoJson.h>
#include <ESP8266WiFi.h>
#include <ESP8266mDNS.h>
#include <ArduinoOTA.h>
#include <Ticker.h>
#include <PubSubClient.h>
#include <FS.h>
#include "Oasis.h"
#include "State.h"
#include "Status.h"
#include "Command.h"
#include "OasisConstants.h"
#include "Logger.h"

WiFiClient   wifiClient;
PubSubClient mqtt(wifiClient);
char payload[JSON_MEMORY_SIZE];
char HOSTNAME[HOSTNAME_SIZE];
char NODE_IP[IP_SIZE];

Logger logger;
char  logMsg[1024];

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

      if(!inboundData[NODE::LOG].isNull()
          && inboundData[NODE::LOG].as<bool>()){
        logger.write("[MQTT] log was requested");
        logger.readPreviousLog(outboundData);
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

  logger.write("[SERIAL] Reconfiguring CONNECTION setup ...");
  Serial.print("Enter WiFi SSID: ");
  ssid = Serial.readStringUntil('\n');
  Serial.print("\nEnter WiFi PASSWORD:");
  passwd = Serial.readStringUntil('\n');

  //removing unecessary ending char
  ssid.trim();
  passwd.trim();

  sprintf(logMsg, "[WIFI] New WiFi SSID: %s", ssid.c_str());
  logger.write(logMsg);

  sprintf(logMsg, "[WIFI] New WiFi PASSWORD: %s", passwd.c_str());
  logger.write(logMsg);

  JsonObject CONFIG = wifi.createNestedObject(NODE::CONFIG);
  CONFIG[NODE::SSID]     = ssid;
  CONFIG[NODE::PASSWORD] = passwd;

  state.save(wifi);

  logger.write("[SERIAL] Ended CONNECTION setup");
}

void setupWifi() {

  sprintf(logMsg, "[WIFI] MAC: %s", WiFi.macAddress().c_str());
  logger.write(logMsg);

  sprintf(logMsg, "[WIFI] Connecting to SSID: %s", state.getSsid());
  logger.write(logMsg);

  WiFi.mode(WIFI_STA);
  WiFi.begin(state.getSsid(), state.getPassword());

  while (WiFi.waitForConnectResult() != WL_CONNECTED) {
    sprintf(logMsg, "[WIFI] Connection Failed! Rebooting in %i seconds...",
                  state.getWifiRetryConnectionDelay() / 1000);
    logger.write(logMsg);

    delay(state.getWifiRetryConnectionDelay());

    serialCommands(); // just in case wifi was badly configured

    ESP.restart();
  }

  IPAddress ip = WiFi.localIP();
  sprintf(NODE_IP, "%d.%d.%d.%d", ip[0],ip[1],ip[2],ip[3]);

  sprintf(logMsg, "[WIFI] IP address: %s", NODE_IP);
  logger.write(logMsg);

  sprintf(logMsg, "[WIFI] Connecting to SSID: %s", state.getSsid());
  logger.write(logMsg);
}

/* DO NOT CHANGE this function name - Arduino hook */
void setup() {
  state.load();

  Serial.begin(state.getSerialBaudRate());
  Serial.setTimeout(3000);
  //while (!Serial) continue;

  logger.init(state.getBootCount());

  status.updatePorts(state);
  command.updatePorts(state);

  JsonObject cmd = state.getCommand();
  if(cmd[NODE::WATER]){
    logger.write("[OASIS] Turn off water for security purpose");
    cmd[NODE::WATER] = false;
  }
  command.execute(state, cmd);

  state.print();

  sprintf(HOSTNAME, "oasis-%06x", ESP.getChipId());
  sprintf(logMsg, "[OASIS] Hostname: %s", HOSTNAME);
  logger.write(logMsg);
  sprintf(logMsg, "[OASIS] Boot Count: %i", state.getBootCount());
  logger.write(logMsg);
  sprintf(logMsg, "[OASIS] Firmware version: %s", FIRMWARE_VERSION);
  logger.write(logMsg);
  logger.write("[OASIS] Starting Setup");

  setupWifi();

  ArduinoOTA.setHostname(HOSTNAME);
  ArduinoOTA.setPort(state.getOtaPort());
  ArduinoOTA.onStart([]() {
    logger.write("[OTA] Starting");
  });
  ArduinoOTA.onEnd([]() {
    logger.write("[OTA] Update finished! Rebooting");
  });
  ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
    Serial.printf("[OTA] Progress: %u%%\r", (progress / (total / 100)));
  });
  ArduinoOTA.onError([](ota_error_t error) {
    sprintf(logMsg, "[OTA] Error[%u]: ", error);
    logger.write(logMsg);

    if (error == OTA_AUTH_ERROR) {
      logger.write("[OTA] Auth Failed");
    } else if (error == OTA_BEGIN_ERROR) {
      logger.write("[OTA] Begin Failed");
    } else if (error == OTA_CONNECT_ERROR) {
      logger.write("[OTA] Connect Failed");
    } else if (error == OTA_RECEIVE_ERROR) {
      logger.write("[OTA] Receive Failed");
    } else if (error == OTA_END_ERROR) {
      logger.write("[OTA] End Failed");
    }
  });
  ArduinoOTA.begin();
  mqtt.setServer(state.getMqttServer(),
                 state.getMqttPort());
  mqtt.setCallback(onMqttMessage);
  mqttReconnect();

  // Oasis is up and running, notify first heartbeat
  char message[HEARTBEAT_MESSAGE_SIZE];
  sprintf(message, "{\"%s\":\"oasis-%06x\", \"startup\": true}",NODE::NODE_ID,ESP.getChipId());
  mqtt.publish(state.getMqttHeartBeatTopic(), message);

  // For sure, we do not need short heartbeat
  if(state.getHeartBeatPeriod() > THRESHOLD_DISABLE_HEARTBEAT){
    heartBeatTicker.attach_ms(state.getHeartBeatPeriod(), heartBeat);
  }else{
    logger.write("[OASIS] HeartBeat not enabled");
  }
  logger.write("[OASIS] Setup Completed");
  listLocalFiles();
}

void mqttReconnect() {
  mqtt.disconnect();

  // Loop until we're reconnected
  while (!mqtt.connected()) {
    logger.write("[MQTT] Attempting connection");
    if (mqtt.connect(HOSTNAME,MQTT_WILL_TOPIC,MQTT_WILL_QOS,MQTT_WILL_RETAIN,MQTT_WILL_MESSAGE)) {
      logger.write("[MQTT] connected");
      mqtt.subscribe(state.getMqttInboundTopic());
    } else {
      sprintf(logMsg, "[MQTT] failed, rc=%i. Try again in %i seconds", mqtt.state(),state.getWifiRetryConnectionDelay() / 1000);
      logger.write(logMsg);
      delay(state.getWifiRetryConnectionDelay());
    }
  }
}

void heartBeat() {
  char message[HEARTBEAT_MESSAGE_SIZE];
  sprintf(message, "{\"%s\":\"oasis-%06x\"}",NODE::NODE_ID,ESP.getChipId());
  mqtt.publish(state.getMqttHeartBeatTopic(), message);
}

void listLocalFiles(){
  String str = "[FILE] Listing local files: \r\n";
  Dir dir = SPIFFS.openDir("/");
  while (dir.next()) {
      str += "[FILE] "+ dir.fileName()+ "\t"+ dir.fileSize()+ " bytes\r\n";
  }
  logger.write(str.c_str());
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
      case 10: //ENTER
      case 13: //ENTER
          Serial.println();
          break;
      case 27: //ESC
          logger.write("[SERIAL] Reseting state to initial configuration!");
          state.remove();
          state.resetBootCount();
          logger.removeAllLogFiles();
          break;
      case 32: //Space bar
          sprintf(logMsg, "[SERIAL] Hostname: %s", HOSTNAME);
          logger.write(logMsg);
          sprintf(logMsg, "[SERIAL] Boot Count: %i", state.getBootCount());
          logger.write(logMsg);
          sprintf(logMsg, "[SERIAL] Firmware: %s", FIRMWARE_VERSION);
          logger.write(logMsg);
          sprintf(logMsg, "[SERIAL] MAC:  %s", WiFi.macAddress().c_str());
          logger.write(logMsg);
          sprintf(logMsg, "[SERIAL] IP: %s",NODE_IP);
          logger.write(logMsg);

          state.print();
          break;
      case 99: //c
          {
            setupNewWifi();
          }
          break;
      case 100: //d
          logger.write("[SERIAL] Listing local files");
          listLocalFiles();
          break;
      case 63: //?
      case 104: //h (HELP!)
          Serial.println("[SERIAL] COMMAND HELP:");
          Serial.println("'ESC': reset to default config");
          Serial.println("'Space bar': print state");
          Serial.println("'?' or 'h': help");
          Serial.println("'c': setup new WiFi");
          Serial.println("'d': list local files");
          Serial.println("'l': print log configuration");
          Serial.println("'m': print last log file");
          Serial.println("'r': reboot command");
          break;
      case 108: //l
          logger.write("[SERIAL] Print log config:");
          logger.print();
          break;
      case 109: //m
          logger.write("[SERIAL] Print last log file:");
          serializeJsonPretty(logger.readPreviousLog(), Serial);
          break;
      case 114: //r
          logger.write("[SERIAL] Rebooting ...");
          ESP.restart();
          break;
      default:
          sprintf(logMsg, "[SERIAL] Unknown command: %d", incomingByte);
          logger.write(logMsg);
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
