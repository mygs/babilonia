#ifndef CapacitiveMoisture_h
#define CapacitiveMoisture_h
#include <Arduino.h>
#include "OasisConstants.h"

class CapacitiveMoisture {
private:
  const int PIN_ANALOGIC = A0; // pin were sensor is connected
public:
  CapacitiveMoisture();
  int read(int PIN[], int x);
  /*TODO: when fertilizer and salt ions leach into the plaster*/
  void calibration();
};
#endif
