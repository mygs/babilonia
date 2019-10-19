#include "CapacitiveMoisture.h"
using namespace std;

CapacitiveMoisture::CapacitiveMoisture(){
  pinMode(PIN, INPUT);
}

int CapacitiveMoisture::read(){
  return analogRead(PIN);
}
