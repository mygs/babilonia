#!/usr/bin/python3
from nabucodonosor import DB

class OasisData(DB.Model):
    TIMESTAMP = DB.Column(DB.String(64), primary_key=True)
    NODE_ID = DB.Column(DB.String(32), primary_key=True)
    DATA = DB.Column(DB.JSON, nullable=True)
