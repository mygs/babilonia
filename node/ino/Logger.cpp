#include "Logger.h"


// internal strings stored in flash for efficiency
const char _logFilenameFormat[] PROGMEM = "%s/%d%02d%02d";

Logger::Logger(){
  if (!SPIFFS.begin()) {
      Serial.println("Failed to mount file system");
  }
}

void Logger::init()
{
    this->process();
}

void Logger::process()
{
    const unsigned long currentMillis = millis();
    if (currentMillis - this->_lastProcess > this->_processInterval || this->_processNow){
        const time_t now = time(nullptr);
        const time_t today = now / 86400 * 86400; // remove the time part
        if (this->_today != today){
          // we have switched to another day, let's run the required updates
            this->_today = today;
            this->_updateCurPath();
            this->_runRotation();
        }

        this->_lastProcess = currentMillis;
        this->_processNow = false;
    }
}
