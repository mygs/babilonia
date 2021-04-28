#ifndef Logger_h
#define Logger_h
#include <Arduino.h>
#include <FS.h> // Include the SPIFFS library

using namespace std;

#define LOG_DIR "/log"

class Logger{
protected:
  unsigned long _lastProcess = 0;  /**< last processing millis() */
  const uint16_t _processInterval; /**< ms between processing runs */
  uint16_t _logFilesToKeep;
  uint16_t _maxLogFileSize;
  bool _processNow = true;         /**< force processing now, even if the processing interval hasn't passed */
  char _curPath[32];               /**< path for today's file */

  void _runRotation();
  void _updateCurPath();

public:
  Logger(uint16_t logFilesToKeep = 2,uint16_t maxLogFileSize = 1000, uint16_t processInterval = 3600000);
  void init();
  void process();
};
#endif
