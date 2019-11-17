#!/usr/bin/python3
# -*- coding: utf-8 -*-
class SoilMoistureAnalytics:

    MUX_PORT_THRESHOLD_IDLE=50
    MUX_PORT_THRESHOLD_DRY=600

    def __init__(self, cfg):
        self.cfg = cfg
