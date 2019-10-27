#include "CapacitiveMoisture.h"
using namespace std;

CapacitiveMoisture::CapacitiveMoisture(){
}

/***
Analog Multiplexers/Demultiplexers (74HC4051)

C B A | CHANNEL
------|--------
L L L | X0
L L H | X1
L H L | X2
L H H | X3
H L L | X4
H L H | X5
H H L | X6
H H H | X7
*/
int CapacitiveMoisture::read(int PIN[], int x){
  int CHANNEL_SELECT_A_PORT = PIN[IDX_CHANNEL_SELECT_A];
  int CHANNEL_SELECT_B_PORT = PIN[IDX_CHANNEL_SELECT_B];
  int CHANNEL_SELECT_C_PORT = PIN[IDX_CHANNEL_SELECT_C];

  pinMode(PIN_ANALOGIC, INPUT);
  pinMode(CHANNEL_SELECT_A_PORT, OUTPUT);
  pinMode(CHANNEL_SELECT_B_PORT, OUTPUT);
  pinMode(CHANNEL_SELECT_C_PORT, OUTPUT);

  switch (x) {
    case 0:
      digitalWrite(CHANNEL_SELECT_A_PORT, LOW);
      digitalWrite(CHANNEL_SELECT_B_PORT, LOW);
      digitalWrite(CHANNEL_SELECT_C_PORT, LOW);
      break;
    case 1:
      digitalWrite(CHANNEL_SELECT_A_PORT, HIGH);
      digitalWrite(CHANNEL_SELECT_B_PORT, LOW);
      digitalWrite(CHANNEL_SELECT_C_PORT, LOW);
      break;
    case 2:
      digitalWrite(CHANNEL_SELECT_A_PORT, LOW);
      digitalWrite(CHANNEL_SELECT_B_PORT, HIGH);
      digitalWrite(CHANNEL_SELECT_C_PORT, LOW);
      break;
    case 3:
      digitalWrite(CHANNEL_SELECT_A_PORT, HIGH);
      digitalWrite(CHANNEL_SELECT_B_PORT, HIGH);
      digitalWrite(CHANNEL_SELECT_C_PORT, LOW);
      break;
    case 4:
      digitalWrite(CHANNEL_SELECT_A_PORT, LOW);
      digitalWrite(CHANNEL_SELECT_B_PORT, LOW);
      digitalWrite(CHANNEL_SELECT_C_PORT, HIGH);
      break;
    case 5:
      digitalWrite(CHANNEL_SELECT_A_PORT, HIGH);
      digitalWrite(CHANNEL_SELECT_B_PORT, LOW);
      digitalWrite(CHANNEL_SELECT_C_PORT, HIGH);
      break;
    case 6:
      digitalWrite(CHANNEL_SELECT_A_PORT, LOW);
      digitalWrite(CHANNEL_SELECT_B_PORT, HIGH);
      digitalWrite(CHANNEL_SELECT_C_PORT, HIGH);
      break;
    case 7:
      digitalWrite(CHANNEL_SELECT_A_PORT, HIGH);
      digitalWrite(CHANNEL_SELECT_B_PORT, HIGH);
      digitalWrite(CHANNEL_SELECT_C_PORT, HIGH);
      break;
    default:
      break;
  }
  return analogRead(PIN_ANALOGIC);
}
