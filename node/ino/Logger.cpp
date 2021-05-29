#include "Logger.h"

// internal strings stored in flash for efficiency
const char _logFilenameFormat[] PROGMEM = LOG_DIR"/%d";


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
    unsigned long logToRemove = this->_curBootCount - this->_logFilesToKeep;
    while (directory.next()){
      int logId;
      if (sscanf(directory.fileName().c_str(), _logFilenameFormat, &logId) == 1) {
        if(logId <= logToRemove){
          // check if file is too old and, if so, delete it
          Serial.printf("[ROTATION] removing file: %s\r\n",directory.fileName().c_str());
          SPIFFS.remove(directory.fileName());
        }else{
          Serial.printf("[ROTATION] keeping file: %s\r\n",directory.fileName().c_str());
        }
      } else {
        Serial.printf("[ROTATION] Could not extract log id from %s\r\n",directory.fileName().c_str());
      }
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

size_t Logger::write(const char* value){
    Serial.println(value);
    int len = sizeof(value);
    File f = SPIFFS.open(this->_curPath, "a"); //append
    f.println(value);
    f.close();
    return len;
}

size_t Logger::readPreviousLog(){
    char filePath[32];
    sprintf_P(filePath, _logFilenameFormat, this->_curBootCount-1);

    if (!SPIFFS.exists(filePath))
        return 0;

    File logFile = SPIFFS.open(filePath, "r");

    size_t filesize = logFile.size(); //the size of the file in bytes
    char debugLogData[filesize];
    logFile.read((uint8_t *)debugLogData, sizeof(debugLogData));

    logFile.close();

    Serial.println(debugLogData);

    return filesize;
}
