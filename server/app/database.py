#!/usr/bin/python3
import sqlite3 as sql
import time
import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import scoped_session, sessionmaker

database_name="nodes.db"
project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, database_name))

engine = create_engine(database_file, convert_unicode=True)
metadata = MetaData()
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
def init_db():
    metadata.create_all(bind=engine)

def insert_data(values):
    con = sql.connect(os.path.join(project_dir, database_name))
    cur = con.cursor()
    cur.execute("""INSERT INTO DATA (ID,TIMESTAMP,STATUS_DHT,MEASURED_MOISTURE,CALCULATE_TEMPERATURE,MEASURED_TEMPERATURE,
                                    MEASURED_HUMIDITY,STATUS_FAN, STATUS_LIGHT)
                    VALUES (?,?,?,?,?,?,?,?,?)""",
                (values['id'],int(time.time()),values['sd'],values['mm'],values['ct'],values['mt'],values['mh'],values['sf'],values['sl']))
    con.commit()
    con.close()

def retrieve_cfg(values):
    con = sql.connect(os.path.join(project_dir, database_name))
    cur = con.cursor()
    cur.execute("""SELECT TEMPERATURE_THRESHOLD,MASK_CRON_LIGHT_ON,
                          MASK_CRON_LIGHT_OFF,MASK_CRON_CTRL,LAST_UPDATE
                    FROM NODECFG WHERE ID = ?""", (values['id'],))
    conf = ""
    for row in cur.fetchall():
        conf = "id:"+values['id']+";temp:"+str(row[0])+";"
        # ask node to reboot because we are sending new crontab parameters
        conf += "mclon:"+str(row[1])+";mcloff:"+str(row[2])+";mcctrl:"+str(row[3])+";"
        conf += "cmd:0"
    cur.execute("UPDATE NODECFG SET LAST_UPDATE = ? WHERE ID = ?", (int(time.time()),values['id'],))
    con.commit()
    con.close()
    return conf
