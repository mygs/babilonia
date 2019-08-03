#!/usr/bin/python3
import time
import os
import MySQLdb as mdb
import simplejson as json

project_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(project_dir, 'config.json'), "r") as json_data_file:
    cfg = json.load(json_data_file)

HOST   = cfg["DATABASE"]["HOST"]
USER   = cfg["DATABASE"]["USER"]
PWD    = cfg["DATABASE"]["PASSWORD"]
SCHEMA = cfg["DATABASE"]["SCHEMA"]

def update_oasis_heartbeat(node_id, timestamp):
    con = mdb.connect(HOST, USER, PWD, SCHEMA)
    with con:
        cur = con.cursor()
        cur.execute("""INSERT INTO OASIS_HEARTBEAT (NODE_ID, LAST_UPDATE)
                    VALUES (%s,%s) ON DUPLICATE KEY UPDATE LAST_UPDATE=%s""",
                    (node_id,timestamp,timestamp))
        con.commit();
