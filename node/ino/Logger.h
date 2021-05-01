#ifndef Logger_h
#define Logger_h
#include <Arduino.h>
#include <FS.h> // Include the SPIFFS library

using namespace std;

#define LOG_DIR "/log"

class Logger{
protected:
  unsigned long _curBootCount;
  uint16_t _logFilesToKeep;
  uint16_t _maxLogFileSize;
  char _curPath[32];

  void _runRotation();
  void _updateCurPath();

public:
  Logger(uint16_t logFilesToKeep = 2,uint16_t maxLogFileSize = 1000);
  void init(unsigned long bootCount);
  void print();
  size_t write(char* value);
  void removeAllLogFiles();
};
#endif
