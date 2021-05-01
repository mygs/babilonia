#include "Logger.h"


Logger::Logger(unsigned long curBootCount, uint16_t logFilesToKeep,uint16_t maxLogFileSize)
    : _curBootCount(curBootCount),
      _logFilesToKeep(logFilesToKeep),
      _maxLogFileSize(maxLogFileSize){
    if (!SPIFFS.begin()) {
        Serial.println("Failed to mount file system");
    }
}

void Logger::init(){
  unsigned long bootCount = 0;

  if (bootCount != this->_curBootCount){
      this->_updateCurPath();
      this->_runRotation();
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
