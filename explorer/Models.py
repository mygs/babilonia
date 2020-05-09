#!/usr/bin/python3
# -*- coding: utf-8 -*-
from flask_sqlalchemy import SQLAlchemy
DB = SQLAlchemy()

class Prices(DB.Model):
    __tablename__ = 'PRICES'
    SOURCE = DB.Column(DB.String(32), primary_key=True)
    DATE = DB.Column(DB.DATE, primary_key=True)
    DATA = DB.Column(DB.JSON, nullable=True)
    def __init__(self, SOURCE, DATE, DATA):
        self.SOURCE = SOURCE
        self.DATE = DATE
        self.DATA = DATA
    def __repr__(self):
        return '<Prices source:{} date:{}>'.format(self.SOURCE, self.DATE)
    def toJson(self):
        return {"SOURCE":self.SOURCE,"DATE":self.DATE,"DATA":self.DATA}
    def data(self):
        return self.DATA
