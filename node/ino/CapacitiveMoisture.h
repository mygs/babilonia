#ifndef CapacitiveMoisture_h
#define CapacitiveMoisture_h
#include "Arduino.h"

class CapacitiveMoisture {
private:
  uint8_t _pin;
public:
  CapacitiveMoisture(uint8_t pin);
  long read();
};
#endif
