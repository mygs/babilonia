#ifndef Logger_h
#define Logger_h
#include <time.h>
#include <FS.h> // Include the SPIFFS library

using namespace std;

#define LOG_DIR "/log"

class Logger{
protected:
  time_t _today = 0;               /**< current date, set in the last processing run */
  unsigned long _lastProcess = 0;  /**< last processing millis() */
  const uint16_t _processInterval; /**< ms between processing runs */
  const uint16_t _daysToKeep;      /**< number of days to keep logs for */
  bool _processNow = true;         /**< force processing now, even if the processing interval hasn't passed */

private:


public:
  Logger();

};
#endif
