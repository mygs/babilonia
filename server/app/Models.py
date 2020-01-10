#!/usr/bin/python3
# -*- coding: utf-8 -*-
from flask_sqlalchemy import SQLAlchemy
DB = SQLAlchemy()

class OasisData(DB.Model):
    __tablename__ = 'OASIS_DATA'
    TIMESTAMP = DB.Column(DB.String(64), primary_key=True)
    NODE_ID = DB.Column(DB.String(32), primary_key=True)
    DATA = DB.Column(DB.JSON, nullable=True)
    def __init__(self, TIMESTAMP, NODE_ID, DATA):
        self.TIMESTAMP = TIMESTAMP
        self.NODE_ID = NODE_ID
        self.DATA = DATA
    def __repr__(self):
        return '<OasisData id:{} time:{}>'.format(self.NODE_ID, self.TIMESTAMP)
    def toJson(self):
        return {"TIMESTAMP":self.TIMESTAMP,"NODE_ID":self.NODE_ID,"DATA":self.DATA}
    def data(self):
        return self.DATA['DATA']


class OasisHeartbeat(DB.Model):
    __tablename__ = 'OASIS_HEARTBEAT'
    NODE_ID = DB.Column(DB.String(32), primary_key=True)
    LAST_UPDATE = DB.Column(DB.String(64), nullable=False)
    def __repr__(self):
        return '<OasisHeartbeat id:{} time:{}>'.format(self.NODE_ID, self.LAST_UPDATE)
    def toJson(self):
        return {"NODE_ID":self.NODE_ID,"LAST_UPDATE":self.LAST_UPDATE}

class User(DB.Model):
    __tablename__ = 'USER'
    USERNAME = DB.Column(DB.String(8), primary_key=True)
    PASSWORD = DB.Column(DB.String(8))
    def __init__(self, USERNAME, PASSWORD):
        self.USERNAME = USERNAME
        self.PASSWORD = PASSWORD
    def __repr__(self):
        return '<User name:{} password:{}>'.format(self.USERNAME, self.PASSWORD)
    def is_authenticated(self):
        return True
    def is_active(self):
        return True
    def is_anonymous(self):
        return False
    def get_id(self):
        return self.USERNAME
    def toJson(self):
        return {"USERNAME":self.USERNAME,"PASSWORD":self.PASSWORD}

class OasisAnalytic(DB.Model):
    __tablename__ = 'OASIS_ANALYTIC'
    TIMESTAMP = DB.Column(DB.String(64), primary_key=True)
    NODE_ID = DB.Column(DB.String(32), primary_key=True)
    TYPE = DB.Column(DB.String(16), nullable=False)
    DATA = DB.Column(DB.JSON, nullable=True)
    def __init__(self, TIMESTAMP, NODE_ID, TYPE, DATA):
        self.TIMESTAMP = TIMESTAMP
        self.NODE_ID = NODE_ID
        self.TYPE = TYPE
        self.DATA = DATA
    def __repr__(self):
        return '<OasisTraining id:{} time:{}>'.format(self.NODE_ID, self.TIMESTAMP)
    def toJson(self):
        return {"TIMESTAMP":self.TIMESTAMP,
                "NODE_ID":self.NODE_ID,
                "TYPE":self.TYPE,
                "DATA":self.DATA}
    def data(self):
        return self.DATA
