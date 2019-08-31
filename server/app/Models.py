#!/usr/bin/python3
# -*- coding: utf-8 -*-
from flask_sqlalchemy import SQLAlchemy
DB = SQLAlchemy()

class OasisData(DB.Model):
    __tablename__ = 'OASIS_DATA'
    TIMESTAMP = DB.Column(DB.String(64), primary_key=True)
    NODE_ID = DB.Column(DB.String(32), primary_key=True)
    DATA = DB.Column(DB.JSON, nullable=True)
    def __repr__(self):
        return '<OasisData id:{} time:{}>'.format(self.NODE_ID, self.TIMESTAMP)


class OasisHeartbeat(DB.Model):
    __tablename__ = 'OASIS_HEARTBEAT'
    NODE_ID = DB.Column(DB.String(32), primary_key=True)
    LAST_UPDATE = DB.Column(DB.String(64), nullable=False)
    def __repr__(self):
        return '<OasisHeartbeat id:{} time:{}>'.format(self.NODE_ID, self.LAST_UPDATE)

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
