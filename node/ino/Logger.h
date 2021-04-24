#ifndef Logger_h
#define Logger_h
#include <Arduino.h>
#include <time.h>
#include <FS.h> // Include the SPIFFS library

using namespace std;

#define LOG_DIR "/log"


struct LogData{
    time_t timestampUTC; /**< creation time in UTC */
    const char* data;
};

class Logger{
protected:
  time_t _today = 0;               /**< current date, set in the last processing run */
  unsigned long _lastProcess = 0;  /**< last processing millis() */
  const uint16_t _processInterval; /**< ms between processing runs */
  const uint16_t _daysToKeep;      /**< number of days to keep logs for */
  bool _processNow = true;         /**< force processing now, even if the processing interval hasn't passed */
  char _directory[21];             /**< base directory for log files */
  char _curPath[32];               /**< path for today's file */



  void _pathFromDate(char *output, time_t date);
  void _updateCurPath();
  void _runRotation();
  static time_t _filenameToDate(const char *filename);
  static time_t _timegm(struct tm *tm);

private:


public:
  /**
   * Default constructor for Logger.
   *
   * @param directory        char array with the base directory where files will be stored. Should not include
   *                         trailing slash and should be 20 characters or less.
   * @param daysToKeep       number of days to keep in flash. Once files are past this age, they are deleted.
   * @param processInterval  milliseconds between file directory updates and file rotation.
   */
  Logger(const char *directory, uint16_t daysToKeep = 7, uint16_t processInterval = 1000);
  void init();
  void process();
  size_t write(const char* value);

};
#endif
