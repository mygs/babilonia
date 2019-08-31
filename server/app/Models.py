#!/usr/bin/python3
# -*- coding: utf-8 -*-
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
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

class User(UserMixin):

    def __init__(self, id):
        self.id = id
        self.name = "user" + str(id)
        self.password = self.name

    def __repr__(self):
        return "%d/%s/%s" % (self.id, self.name, self.password)
