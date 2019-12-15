#!/usr/bin/python3
# -*- coding: utf-8 -*-
import json

class SoilMoistureAnalytics:

    MUX_PORT_THRESHOLD_IDLE=50
    MUX_PORT_THRESHOLD_DRY=600

    def status(self, level):
        if level < self.MUX_PORT_THRESHOLD_IDLE:
            return "moisture-disable"
        else:
            #TODO: put some brain in here
            return "moisture-wet"

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
            sort_keys=True, indent=4)
