#!/usr/bin/python
import sqlite3 as sql
import time

def insert_data(values):
    con = sql.connect("nodes.db")
    cur = con.cursor()
    cur.execute("""INSERT INTO DATA (ID,TIMESTAMP,STATUS_DHT,CALCULATE_TEMPERATURE,MEASURED_TEMPERATURE,
                                    MEASURED_HUMIDITY,STATUS_FAN, STATUS_LIGHT)
                    VALUES (?,?,?,?,?,?,?,?)""",
                (values['id'],int(time.time()),values['sd'],values['ct'],values['mt'],values['mh'],values['sf'],values['sl']))
    con.commit()
    con.close()

def retrieve_cfg(values):
    conf = ""
    con = sql.connect("nodes.db")
    cur = con.cursor()
    cur.execute("""SELECT FAN,LIGHT,TEMPERATURE_THRESHOLD,MASK_CRON_LIGHT_ON,
                          MASK_CRON_LIGHT_OFF,MASK_CRON_CTRL,LAST_UPDATE
                    FROM NODECFG WHERE ID = ?""", (values['id'],))
    for row in cur.fetchall():
        conf = "id:"+values['id']+";fan:"+str(row[0])+";light:"+str(row[1])+";temp:"+str(row[2])+";"
        conf += "mclon:"+str(row[3])+";mcloff:"+str(row[4])+";mcctrl:"+str(row[5])
    cur.execute("UPDATE NODECFG SET LAST_UPDATE = ? WHERE ID = ?", (int(time.time()),values['id'],))
    con.commit()
    con.close()
    return conf
