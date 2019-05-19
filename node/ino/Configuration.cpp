#include "Configuration.h"
#include "WifiSecurity.h"
#include <FS.h> // Include the SPIFFS library

Configuration::Configuration() {
  // Configuration that we'll store on disk
  this->CONFIG_FILE = "/config.json";

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

  Serial.println("[CONFIG] Loading configuration");

  if (!SPIFFS.exists(CONFIG_FILE)) {
    saveDefaultConfiguration();
  } else {
    loadConfiguration();
  }
}

void Configuration::saveDefaultConfiguration() {
  StaticJsonDocument<512> CONFIG;

  CONFIG["SSID"]                = "babilonia";
  CONFIG["PASSWORD"]            = "1q2w3e4r";
  CONFIG["MQTT_SERVER"]         = "192.168.2.1";
  CONFIG["MQTT_PORT"]           = 1883;
  CONFIG["MQTT_TOPIC_INBOUND"]  = "/oasis-inbound";
  CONFIG["MQTT_TOPIC_OUTBOUND"] = "/oasis-outbound";
  CONFIG["PERIOD"]              = 300;
  JsonObject PIN = CONFIG.createNestedObject("PIN");
  PIN["0"] = "IDLE";
  PIN["1"] = "WATER";
  PIN["2"] = "LIGHT";
  PIN["3"] = "SOIL.X";
  PIN["4"] = "DHT";
  PIN["5"] = "SOIL.1";
  PIN["6"] = "SOIL.2";
  PIN["7"] = "SOIL.3";
  PIN["8"] = "SOIL.4";
  copyFromJsonDocument(CONFIG);

  Serial.println("[CONFIG] creating default configuration file");

  File file = SPIFFS.open(CONFIG_FILE, "w");

  if (!file) {
    Serial.println("[CONFIG] Failed to create configuration file");
    return;
  } else {
    // Serialize JSON to file
    if (serializeJsonPretty(CONFIG, file) == 0) {
      Serial.println("[CONFIG] Failed to write configuration file");
    }
    file.close();
  }
}

void Configuration::loadConfiguration() {
  Serial.println("[CONFIG] Loading existing file configuration");
  StaticJsonDocument<512> CONFIG;

  // Open file for reading
  File file                  = SPIFFS.open(CONFIG_FILE, "r");
  DeserializationError error = deserializeJson(CONFIG, file);

  if (error) {
    #ifdef DEBUG_ESP_OASIS
    Serial.println("\n\n[CONFIG] Failed to read file, using default configuration");
    #endif // ifdef DEBUG_ESP_OASIS
  } else {
    #ifdef DEBUG_ESP_OASIS
    serializeJsonPretty(CONFIG, Serial);
    Serial.println("\n");
    #endif // ifdef DEBUG_ESP_OASIS
    copyFromJsonDocument(CONFIG);
  }
  file.close();
}

void Configuration::copyFromJsonDocument(JsonDocument& CONFIG) {
  this->SSID                = CONFIG["SSID"];
  this->PASSWORD            = CONFIG["PASSWORD"];
  this->MQTT_SERVER         = CONFIG["MQTT_SERVER"];
  this->MQTT_PORT           = CONFIG["MQTT_PORT"];
  this->MQTT_TOPIC_INBOUND  = CONFIG["MQTT_TOPIC_INBOUND"];
  this->MQTT_TOPIC_OUTBOUND = CONFIG["MQTT_TOPIC_OUTBOUND"];
  this->PERIOD              = CONFIG["PERIOD"];
  JsonObject PIN = CONFIG["PIN"];
  this->PIN0 = PIN["0"];
  this->PIN1 = PIN["1"];
  this->PIN2 = PIN["2"];
  this->PIN3 = PIN["3"];
  this->PIN4 = PIN["4"];
  this->PIN5 = PIN["5"];
  this->PIN6 = PIN["6"];
  this->PIN7 = PIN["7"];
  this->PIN8 = PIN["8"];
}
