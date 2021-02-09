#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
from threading import Timer
from time import sleep
if os.uname()[4].startswith("arm"): #This module can only be run on a Raspberry Pi!
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
TIME_TO_DISABLE_SOLENOID_ON =45*60 #secs

class WaterTankManager:
    def __init__(self, logger):
        self.logger = logger
        if os.uname()[4].startswith("arm"):
            gpio.setmode(gpio.BOARD)
            gpio.setwarnings(False)
            gpio.setup(PIN_WATER_TANK_IN, gpio.OUT, initial=gpio.LOW)
            gpio.setup(PIN_WATER_TANK_OUT, gpio.OUT, initial=gpio.LOW)
            gpio.setup(PIN_WATER_LEVEL_SENSOR_A, gpio.IN, pull_up_down=gpio.PUD_DOWN)
            gpio.setup(PIN_WATER_LEVEL_SENSOR_B, gpio.IN, pull_up_down=gpio.PUD_DOWN)
            self.logger.info("[WaterTankManager] setup completed.")
        else:
            self.logger.info("[WaterTankManager] setup completed. Fake GPIO")
            self.FAKE_WATER_TANK_IN = 0
            self.FAKE_WATER_TANK_OUT = 0


    def get_current_sensor_level(self):
        response = {}
        if os.uname()[4].startswith("arm"):
            response['WATER_LEVEL_SENSOR_A'] = gpio.input(PIN_WATER_LEVEL_SENSOR_A)
            response['WATER_LEVEL_SENSOR_B'] = gpio.input(PIN_WATER_LEVEL_SENSOR_B)
        else:
            response['WATER_LEVEL_SENSOR_A'] = 0
            response['WATER_LEVEL_SENSOR_B'] = 0

        return response

    def get_level_description(self):
        description = "ERROR"
        if gpio.input(PIN_WATER_LEVEL_SENSOR_A) == 0:
             if gpio.input(PIN_WATER_LEVEL_SENSOR_B) == 0:
                 description = "FILL"
        else:
             if gpio.input(PIN_WATER_LEVEL_SENSOR_B) == 0:
                description = "HALF"
             else:
                description = "FULL"
        return description

    def get_current_solenoid_status(self):
        response = {}
        if os.uname()[4].startswith("arm"):
            response['GUI_DESCRIPTION'] = self.get_level_description()
            response['WATER_TANK_IN'] = gpio.input(PIN_WATER_TANK_IN)
            response['WATER_TANK_OUT'] = gpio.input(PIN_WATER_TANK_OUT)
            if gpio.input(PIN_WATER_LEVEL_SENSOR_B) == 1:
                response['WATER_TANK_IN_DISABLE'] = True
            else:
                response['WATER_TANK_IN_DISABLE'] = False
        else:
            response['WATER_TANK_IN'] = self.FAKE_WATER_TANK_IN
            response['WATER_TANK_OUT'] = self.FAKE_WATER_TANK_OUT
            response['WATER_TANK_IN_DISABLE'] = False
            response['GUI_DESCRIPTION'] = "HALF"
        return response

    def monitorTankLevel(self):
        if os.uname()[4].startswith("arm"):
            bouncetime = 15*60*1000 # 15 min delay
            gpio.add_event_detect(PIN_WATER_LEVEL_SENSOR_A, gpio.BOTH, callback=self.shouldStartFillingWaterTank, bouncetime=bouncetime)
            gpio.add_event_detect(PIN_WATER_LEVEL_SENSOR_B, gpio.BOTH, callback=self.shouldStopFillingWaterTank, bouncetime=bouncetime)

    def shouldStartFillingWaterTank(self, channel):
        if not gpio.input(PIN_WATER_LEVEL_SENSOR_A) and not gpio.input(PIN_WATER_LEVEL_SENSOR_B):
            self.logger.info("[WaterTankManager] START filling water tank")
            gpio.output(PIN_WATER_TANK_IN, gpio.HIGH)

    def shouldStopFillingWaterTank(self, channel):
        if gpio.input(PIN_WATER_LEVEL_SENSOR_B):
            self.logger.info("[WaterTankManager] STOP filling water tank")
            gpio.output(PIN_WATER_TANK_IN, gpio.LOW)

    def changeStateWaterTankIn(self, state):
        if state:
            self.logger.info("[WaterTankManager] Manually STARTED filling water tank")
            if os.uname()[4].startswith("arm"):
                gpio.output(PIN_WATER_TANK_IN, gpio.HIGH)
            else:
                self.FAKE_WATER_TANK_IN = 1
            timer_thread = Timer(TIME_TO_DISABLE_SOLENOID_ON, self.changeStateWaterTankIn, [False])
            timer_thread.start()
        else:
            self.logger.info("[WaterTankManager] Manually STOPED filling water tank")
            if os.uname()[4].startswith("arm"):
                gpio.output(PIN_WATER_TANK_IN, gpio.LOW)
            else:
                self.FAKE_WATER_TANK_IN = 0

    def changeStateWaterTankOut(self, state):
        if state:
            self.logger.info("[WaterTankManager] Manually STARTED using water tank")
            if os.uname()[4].startswith("arm"):
                gpio.output(PIN_WATER_TANK_OUT, gpio.HIGH)
            else:
                self.FAKE_WATER_TANK_OUT = 1
            timer_thread = Timer(TIME_TO_DISABLE_SOLENOID_ON, self.changeStateWaterTankOut, [False])
            timer_thread.start()
        else:
            self.logger.info("[WaterTankManager] Manually STOPED using water tank")
            if os.uname()[4].startswith("arm"):
                gpio.output(PIN_WATER_TANK_OUT, gpio.LOW)
            else:
                self.FAKE_WATER_TANK_OUT = 0

    def disableWaterTankInAndOut(self):
        self.logger.info("[WaterTankManager] Turn off water tank solenoids for security purpose!")
        if os.uname()[4].startswith("arm"):
            gpio.output(PIN_WATER_TANK_IN, gpio.LOW)
            gpio.output(PIN_WATER_TANK_OUT, gpio.LOW)
        else:
            self.FAKE_WATER_TANK_IN = 0
            self.FAKE_WATER_TANK_OUT = 0

if __name__ == '__main__':
    print("*** STARTING Water Tank Manager Test ***")
    app = WaterTankManager()
    app.monitorTankLevel()
    while True:
        time.sleep(3)
        print("*")
