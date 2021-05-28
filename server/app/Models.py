#!/usr/bin/python3
# -*- coding: utf-8 -*-
import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from flask_login import UserMixin

DB = SQLAlchemy()

class OasisData(DB.Model):
    __tablename__ = 'OASIS_DATA'
    TIMESTAMP = DB.Column(DB.Integer, primary_key=True)
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
    def config(self):
        return self.DATA['DATA']["NODE"]
    def capacitive_moisture(self, moisture):
        self.DATA["DATA"]["CAPACITIVEMOISTURE"]= moisture

class OasisHeartbeat(DB.Model):
    __tablename__ = 'OASIS_HEARTBEAT'
    NODE_ID = DB.Column(DB.String(32), primary_key=True)
    LAST_UPDATE = DB.Column(DB.Integer, nullable=False)
    QUARANTINE = DB.Column(DB.Boolean, nullable=False)
    def __repr__(self):
        return '<OasisHeartbeat id:{} time:{} quarantine:{}>'.format(self.NODE_ID, self.LAST_UPDATE,self.QUARANTINE)
    def toJson(self):
        return {"NODE_ID":self.NODE_ID,"LAST_UPDATE":self.LAST_UPDATE,"QUARANTINE":self.QUARANTINE}
    def quarantine(self):
        return self.QUARANTINE #Python3: False == 0 and True == 1.  Python2.x this is not guaranteed

class Manager(UserMixin):
    def __init__(self, USERNAME):
        self.id = USERNAME

class User(DB.Model):
    __tablename__ = 'USER'
    USERNAME = DB.Column(DB.String(8), primary_key=True)
    PASSWORD = DB.Column(DB.String(8))
    def __init__(self, USERNAME, PASSWORD=None):
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

class OasisTraining(DB.Model):
    __tablename__ = 'OASIS_TRAINING'
    NODE_ID = DB.Column(DB.String(32), primary_key=True)
    VALUE = DB.Column(DB.String(32), primary_key=True)
    MESSAGE_ID = DB.Column(DB.String(32), nullable=False)
    TIMESTAMP = DB.Column(DB.Integer, nullable=False)
    DATA = DB.Column(DB.JSON, nullable=True)
    def __init__(self, NODE_ID, VALUE, MESSAGE_ID, TIMESTAMP, DATA):
        self.NODE_ID = NODE_ID
        self.VALUE = VALUE
        self.MESSAGE_ID = MESSAGE_ID
        self.TIMESTAMP = TIMESTAMP
        self.DATA = DATA
    def __repr__(self):
        return '<OasisTraining id:{} value:{} data: {}>'.format(self.NODE_ID, self.VALUE, self.DATA)
    def toJson(self):
        return {"NODE_ID":self.NODE_ID,
                "VALUE":self.VALUE,
                "MESSAGE_ID":self.MESSAGE_ID,
                "TIMESTAMP":self.TIMESTAMP,
                "DATA":self.DATA}

class OasisAnalytic(DB.Model):
    __tablename__ = 'OASIS_ANALYTIC'
    TIMESTAMP = DB.Column(DB.Integer, primary_key=True)
    TYPE = DB.Column(DB.String(32), primary_key=True)
    DATA = DB.Column(DB.JSON, nullable=True)
    def __init__(self, TIMESTAMP, TYPE, DATA):
        self.TIMESTAMP = TIMESTAMP
        self.TYPE = TYPE
        self.DATA = DATA
    def __repr__(self):
        return '<OasisAnalytic time:{} type:{}>'.format(self.TIMESTAMP, self.TYPE)
    def toJson(self):
        return {"TIMESTAMP":self.TIMESTAMP,
                "TYPE":self.TYPE,
                "DATA":self.DATA}
    def data(self):
        return self.DATA

# Define and create the table
Base = declarative_base()

class Crop(Base):
    __tablename__ = 'CROP'
    CODE = DB.Column(DB.Integer, primary_key=True)
    DATE = DB.Column(DB.DATE, nullable=False)
    STATUS = DB.Column(DB.String(16), nullable=False)
    NOTES = DB.Column(DB.String(256), nullable=True)

    def __init__(self, DATE, STATUS, NOTES):
        self.DATE = DATE
        self.STATUS = STATUS
        self.NOTES = NOTES
    def __repr__(self):
        return '<Crop code:{} date:{}>'.format(self.CODE, self.DATE)
    def toJson(self):
        return {"CODE":self.CODE,"DATE":self.DATE,
                "STATUS":self.STATUS,"NOTES":self.NOTES}
    def code(self):
        return self.CODE
    def date(self):
        return self.DATE
    def status(self):
        return self.STATUS

class Supplier(Base):
    __tablename__ = 'SUPPLIER'
    NAME = DB.Column(DB.String(64), primary_key=True)
    TYPE = DB.Column(DB.String(32), nullable=True)
    PHONE = DB.Column(DB.String(16), nullable=True)
    EMAIL = DB.Column(DB.String(32), nullable=True)
    CITY = DB.Column(DB.String(32), nullable=True)
    STATE = DB.Column(DB.String(64), nullable=True)
    NOTES = DB.Column(DB.String(256), nullable=True)
    def __init__(self, json):
        self.NAME = json['NAME']
        self.TYPE = json['TYPE']
        self.PHONE =json['PHONE']
        self.EMAIL =json['EMAIL']
        self.CITY = json['CITY']
        self.STATE =json['STATE']
        self.NOTES =json['NOTES']
