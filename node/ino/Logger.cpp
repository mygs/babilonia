#include "Logger.h"

// internal strings stored in flash for efficiency
const char _logFilenameFormat[] PROGMEM = "%s/%d";


Logger::Logger(uint16_t logFilesToKeep,uint16_t maxLogFileSize)
    : _logFilesToKeep(logFilesToKeep),
      _maxLogFileSize(maxLogFileSize){
    if (!SPIFFS.begin()) {
        Serial.println("Failed to mount file system");
    }
}

void Logger::init(unsigned long bootCount)){
  this->_curBootCount = bootCount;
  this->_updateCurPath();
  this->_runRotation();
}

void Logger::_updateCurPath(){
  sprintf_P(this->_curPath,
            _logFilenameFormat,
            LOG_DIR,
            this->_curBootCount);
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
