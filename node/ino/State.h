#ifndef State_h
#define State_h
#include <Arduino.h>
#include <ArduinoJson.h>

using namespace std;

#define STATE_FILE "/state.json"
#define BOOT_COUNT_FILE "/bootCount.dat"
// Use arduinojson.org/assistant to compute the capacity.
#define JSON_MEMORY_SIZE 1024

class State{
private:
  unsigned long bootCount = 0;
  StaticJsonDocument<JSON_MEMORY_SIZE> currentState;
  int diffi(JsonVariant _base, JsonVariant _arrived);
  bool diffb(JsonVariant _base, JsonVariant _arrived);
  const char* diffs(JsonVariant _base, JsonVariant _arrived);
  void mergeState(JsonDocument& arrived);
  void saveDefaultState(JsonDocument& state);
  void updateBootCount();

public:
  State();
  //get configuration
  const char * getMqttServer();
  unsigned long getBootCount();
  int getMqttPort();
  int getHeartBeatPeriod();
  int getSensorCollectDataPeriod();
  int getWifiRetryConnectionDelay();
  int getSerialBaudRate();
  int getOtaPort();
  const char * getMqttHeartBeatTopic();
  const char * getMqttInboundTopic();
  const char * getMqttOutboundTopic();
  const char * getSsid();
  const char * getPassword();
  JsonObject getPinSetup();
  JsonObject getCommand();
  int getLightStatus();
  int getFanStatus();
  int getWaterStatus();
  void loadDefaultState();
  int getSwitchAStatus();
  int getSwitchBStatus();

  //procedures
  void load();
  void save(JsonDocument& newState);

  void remove();
  void resetBootCount();
  void print();
  void getPin(int pin[], const char* DEVICE[], int length);
};
#endif
