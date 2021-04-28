#include "Logger.h"


Logger::Logger(uint16_t logFilesToKeep,uint16_t maxLogFileSize, uint16_t processInterval)
    : _logFilesToKeep(logFilesToKeep),
      _maxLogFileSize(maxLogFileSize),
      _processInterval(processInterval){
    if (!SPIFFS.begin()) {
        Serial.println("Failed to mount file system");
    }
}

void Logger::init(){
    this->process();
}

void Logger::process(){
    const unsigned long currentMillis = millis();
    if (currentMillis - this->_lastProcess > this->_processInterval ||
          this->_processNow){
        if (false){
          // let's run the required updates
            this->_updateCurPath();
            this->_runRotation();
        }

        this->_lastProcess = currentMillis;
        this->_processNow = false;
    }
}

void Logger::_updateCurPath(){
}
/*
void Logger::_checkSize(){
    Dir dir = SPIFFS.openDir(LOG_DIR);
    while (dir.next()){
        dir.fileSize()
    }
}
*/
void Logger::_runRotation(){
    Dir directory = SPIFFS.openDir(LOG_DIR);

    while (directory.next()){
        // check if file is too old and, if so, delete it
        if (false)
            SPIFFS.remove(directory.fileName());
    }
}
