#!/usr/bin/python3
import time
import os
import MySQLdb as mdb
import json

project_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(project_dir, 'config.json'), "r") as json_data_file:
    cfg = json.load(json_data_file)

def insert_data(values):
    con = mdb.connect(cfg["db"]["host"], cfg["db"]["user"], cfg["db"]["password"], cfg["db"]["schema"])
    with con:
        cur = con.cursor()
        cur.execute("""INSERT INTO DATA (ID,TIMESTAMP,STATUS_DHT,MEASURED_MOISTURE,
                                        CALCULATE_TEMPERATURE,MEASURED_TEMPERATURE,
                                        MEASURED_HUMIDITY,STATUS_FAN, STATUS_LIGHT)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (values['id'],int(time.time()),values['sd'],values['mm'],
                     values['ct'],values['mt'],values['mh'],values['sf'],values['sl']))
        con.commit()

def retrieve_cfg(values):
    con = mdb.connect(cfg["db"]["host"], cfg["db"]["user"], cfg["db"]["password"], cfg["db"]["schema"])
    with con:
        cur = con.cursor()
        cur.execute("""SELECT TEMPERATURE_THRESHOLD,MASK_CRON_LIGHT_ON,
                              MASK_CRON_LIGHT_OFF,MASK_CRON_CTRL,LAST_UPDATE
                        FROM NODE WHERE ID = %s""", (values['id'],))
        conf = ""
        for row in cur.fetchall():
            conf = "id:"+values['id']+";temp:"+str(row[0])+";"
            # ask node to reboot because we are sending new crontab parameters
            conf += "mclon:"+str(row[1])+";mcloff:"+str(row[2])+";mcctrl:"+str(row[3])+";"
            conf += "cmd:0"
        cur.execute("UPDATE NODE SET LAST_UPDATE = %s WHERE ID = %s", (int(time.time()),values['id'],))
        con.commit()
        return conf
