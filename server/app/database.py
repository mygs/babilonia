#!/usr/bin/python3
import time
import os
import logging
import logging.config
import MySQLdb as mdb
import simplejson as json
###### create console handler and set level to debug
project_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(project_dir, 'logging.json'), "r") as logging_json_file:
    logging_config = json.load(logging_json_file)
    logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)

project_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(project_dir, 'config.json'), "r") as json_data_file:
    cfg = json.load(json_data_file)

HOST   = cfg["DATABASE"]["HOST"]
USER   = cfg["DATABASE"]["USER"]
PWD    = cfg["DATABASE"]["PASSWORD"]
SCHEMA = cfg["DATABASE"]["SCHEMA"]

def update_oasis_heartbeat(timestamp, node_id):
    con = mdb.connect(HOST, USER, PWD, SCHEMA)
    cur = con.cursor()
    try:
        cur.execute("""INSERT INTO OASIS_HEARTBEAT (NODE_ID,LAST_UPDATE)
                    VALUES (%s,%s) ON DUPLICATE KEY UPDATE LAST_UPDATE=%s""",
                    (node_id,timestamp,timestamp))
        con.commit();
        return 0
    except:
        return -1
    finally:
        cur.close()
        con.close()

def save_oasis_data(timestamp, data):
    node_id = data["NODE_ID"]
    json_data = json.dumps(data)
    con = mdb.connect(HOST, USER, PWD, SCHEMA)
    cur = con.cursor()
    try:
        query = """INSERT INTO OASIS_DATA (TIMESTAMP,NODE_ID,DATA)
                    VALUES ({},{},{})
                    ON DUPLICATE KEY UPDATE DATA={}""".format(timestamp,node_id,json_data,json_data)
        cur.execute(query)
        logger.debug("[database] save_oasis_data >> %s", query)

        con.commit();
        return 0
    except:
        return -1
    finally:
        cur.close()
        con.close()
