#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sqlalchemy
import json
from sqlalchemy.ext.declarative import declarative_base


# Define and create the table
Base = declarative_base()


class Prices(Base):
    __tablename__ = "PRICES"
    SOURCE = sqlalchemy.Column(sqlalchemy.String(16), primary_key=True)
    DATE = sqlalchemy.Column(sqlalchemy.DATE, primary_key=True)
    DATA = sqlalchemy.Column(sqlalchemy.JSON, nullable=True)

    def __init__(self, SOURCE, DATE, DATA):
        self.SOURCE = SOURCE
        self.DATE = DATE
        self.DATA = DATA

    def __repr__(self):
        return "<Prices source:{} date:{}>".format(self.SOURCE, self.DATE)

    def toJson(self):
        return {"SOURCE": self.SOURCE, "DATE": self.DATE, "DATA": self.DATA}

    def data(self):
        return self.DATA
