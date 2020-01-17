#!/usr/bin/python3
# -*- coding: utf-8 -*-
import json
from Models import *
import logging

class SoilMoistureAnalytics:
    #default values
    MUX_PORT_THRESHOLD_IDLE=50
    MUX_PORT_THRESHOLD_DRY=600
    MUX_PORT_THRESHOLD_NOSOIL=680

    def __init__(self, logger):
        self.logger = logger

    def status(self, node_id, port, level):
        analytics = DB.session.query(OasisAnalytic).first()
        self.logger.debug("[SoilMoistureAnalytics] %s", analytics.data())

        if level < self.MUX_PORT_THRESHOLD_IDLE or level > self.MUX_PORT_THRESHOLD_NOSOIL:
            return "moisture-disable"
        else:
            #TODO: put some brain in here
            return "moisture-wet"

    def param(self):
        return {"MUX_PORT_THRESHOLD_IDLE":self.MUX_PORT_THRESHOLD_IDLE,
                "MUX_PORT_THRESHOLD_DRY":self.MUX_PORT_THRESHOLD_DRY,
                "MUX_PORT_THRESHOLD_NOSOIL":self.MUX_PORT_THRESHOLD_NOSOIL}
