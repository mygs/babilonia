#!/usr/bin/python3
# -*- coding: utf-8 -*-
class SoilMoistureAnalytics:

    MUX_PORT_THRESHOLD_IDLE=50
    MUX_PORT_THRESHOLD_DRY=600

    def status(self, level):
        if level < self.MUX_PORT_THRESHOLD_IDLE:
            return "moisture-disable"
        else:
            #TODO: put some brain in here
            return "moisture-wet"
