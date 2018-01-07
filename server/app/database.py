#!/usr/bin/python
import sqlite3 as sql
import time

def insert(data):
    values = dict(item.split(":") for item in data.split(";"))
    con = sql.connect("nodes.db")
    cur = con.cursor()
    cur.execute("INSERT INTO DATA (ID,TIMESTAMP,STATUS_DHT,CALCULATE_TEMPERATURE,MEASURED_TEMPERATURE,MEASURED_HUMIDITY,STATUS_FAN, STATUS_LIGHT) VALUES (?,?,?,?,?,?,?,?)",
                (values['id'],int(time.time()),values['sd'],values['ct'],values['mt'],values['mh'],values['sf'],values['sl']))
    con.commit()
    con.close()
