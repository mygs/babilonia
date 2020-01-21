#!/usr/bin/python3
# -*- coding: utf-8 -*-
import json
from Models import *
import logging

class SoilMoistureAnalytics:
    #default values
    MUX_PORT_THRESHOLD_OFFLINE=50
    MUX_PORT_THRESHOLD_DRY=600
    MUX_PORT_THRESHOLD_NOSOIL=680

    def __init__(self, logger):
        self.logger = logger

    def status(self, node_id, port, level):
        analytics = DB.session.query(OasisAnalytic).first()
        self.logger.debug("[SoilMoistureAnalytics] %s", analytics.data())

        if level < self.MUX_PORT_THRESHOLD_OFFLINE:
            return "moisture-offline"
        elif level > self.MUX_PORT_THRESHOLD_NOSOIL:
            return "moisture-nosoil"
        else:
            #TODO: put some brain in here
            return "moisture-wet"

    def param(self):
        return json.dumps(
            {'MUX_PORT_THRESHOLD_OFFLINE':self.MUX_PORT_THRESHOLD_OFFLINE,
            'MUX_PORT_THRESHOLD_DRY':self.MUX_PORT_THRESHOLD_DRY,
            'MUX_PORT_THRESHOLD_NOSOIL':self.MUX_PORT_THRESHOLD_NOSOIL})
