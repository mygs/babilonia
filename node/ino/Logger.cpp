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

void Logger::init(unsigned long bootCount){
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

void Logger::print(){
     Serial.printf("[LOGGER] directory: %s\r\n",LOG_DIR);
     Serial.printf("[LOGGER] curPath: %s\r\n",this->_curPath);
     Serial.printf("[LOGGER] bootCount: %i\r\n",this->_curBootCount);
     Serial.printf("[LOGGER] logFilesToKeep: %i\r\n",this->_logFilesToKeep);
     Serial.printf("[LOGGER] maxLogFileSize: %i\r\n",this->_maxLogFileSize);

}
void Logger::removeAllLogFiles(){
    Dir logDir = SPIFFS.openDir(LOG_DIR);
    while (logDir.next()){
      SPIFFS.remove(logDir.fileName());
    }
}

size_t Logger::write(char* value){
    int len = sizeof(value);
    File f = SPIFFS.open(this->_curPath, "a");
    f.write((uint8_t *)&value, len);
    f.close();
}
