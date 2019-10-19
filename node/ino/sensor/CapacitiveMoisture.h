#ifndef CapacitiveMoisture_h
#define CapacitiveMoisture_h
#include <Arduino.h>

class CapacitiveMoisture {
private:
  const int PIN = A0; // pin were sensor is connected
public:
  CapacitiveMoisture();
  int read();
  /*TODO: when fertilizer and salt ions leach into the plaster*/
  void calibration();
};
#endif
