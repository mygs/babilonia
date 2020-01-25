#!/usr/bin/python3
# -*- coding: utf-8 -*-
import json
from Models import *
import logging

class SoilMoistureAnalytics:

    def __init__(self, logger, defaults):
        self.logger = logger
        #default values
        self.OFFLINE = defaults["OFFLINE"]
        self.WET = defaults["WET"]
        self.NOSOIL = defaults["NOSOIL"]


    def status(self, node_id, port, level):
        analytics = DB.session.query(OasisAnalytic).first()
        self.logger.debug("[SoilMoistureAnalytics] %s", analytics.data())
        #TODO: put some brain in here
        if level <= self.OFFLINE:
            return "moisture-offline"
        elif level > self.OFFLINE and level <= self.WET:
            return "moisture-wet"
        elif level > self.WET and level < self.NOSOIL:
            return "moisture-dry"
        elif level >= self.NOSOIL:
            return "moisture-nosoil"

    def param(self):
        return json.dumps(
            {'MUX_PORT_THRESHOLD_OFFLINE':self.OFFLINE,
            'MUX_PORT_THRESHOLD_WET':self.WET,
            'MUX_PORT_THRESHOLD_NOSOIL':self.NOSOIL})
