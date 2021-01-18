#!/usr/bin/python3
# -*- coding: utf-8 -*-
import RPi.GPIO as gpio
import time
import logging

# Page 102
# https://www.raspberrypi.org/documentation/hardware/raspberrypi/bcm2835/BCM2835-ARM-Peripherals.pdf
###### Server GPIO setup
#
# o V G o X Y o o o o o o o o o o o o o o
# o o o o o A B o o o o o o o o o o o o o
PIN_WATER_TANK_IN           =10 #X
PIN_WATER_TANK_OUT          =12 #Y
PIN_WATER_LEVEL_SENSOR_A    =11 #A (XKC-Y25-V) => orange cable
PIN_WATER_LEVEL_SENSOR_B    =13 #B (XKC-Y25-V) => yellow cable

class WaterTankManager:
    def __init__(self, logger):
        self.logger = logger
        gpio.setmode(gpio.BOARD)
        gpio.setwarnings(False)
        gpio.setup(PIN_WATER_TANK_IN, gpio.OUT, initial=gpio.LOW)
        gpio.setup(PIN_WATER_TANK_OUT, gpio.OUT, initial=gpio.LOW)
        gpio.setup(PIN_WATER_LEVEL_SENSOR_A, gpio.IN, pull_up_down=gpio.PUD_DOWN)
        gpio.setup(PIN_WATER_LEVEL_SENSOR_B, gpio.IN, pull_up_down=gpio.PUD_DOWN)
        self.logger.info("[WaterTankManager] setup completed")

    def monitorTankLevel(self):
        gpio.add_event_detect(PIN_WATER_LEVEL_SENSOR_A, gpio.BOTH, callback=self.shouldStartFillingWaterTank, bouncetime=100)
        gpio.add_event_detect(PIN_WATER_LEVEL_SENSOR_B, gpio.BOTH, callback=self.shouldStopFillingWaterTank, bouncetime=100)

    def shouldStartFillingWaterTank(self, channel):
        if not gpio.input(PIN_WATER_LEVEL_SENSOR_A):
            self.logger.info("[WaterTankManager] START filling water tank")
            gpio.output(PIN_WATER_TANK_IN, gpio.HIGH)

    def shouldStopFillingWaterTank(self, channel):
        if gpio.input(PIN_WATER_LEVEL_SENSOR_B):
            self.logger.info("[WaterTankManager] STOP filling water tank")
            gpio.output(PIN_WATER_TANK_IN, gpio.LOW)

if __name__ == '__main__':
    print("*** STARTING Water Tank Manager Test ***")
    app = WaterTankManager()
    app.monitorTankLevel()
    while True:
        time.sleep(3)
        print("*")
