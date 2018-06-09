#!/usr/bin/python3
import time
import os
import MySQLdb as mdb
import simplejson as json

project_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(project_dir, 'config.json'), "r") as json_data_file:
    cfg = json.load(json_data_file)

def insert_data(time, values):
    con = mdb.connect(cfg["db"]["host"], cfg["db"]["user"], cfg["db"]["password"], cfg["db"]["schema"])
    with con:
        cur = con.cursor()
        cur.execute("""INSERT INTO DATA (ID,TIMESTAMP,STATUS_DHT,
                                        CALCULATE_TEMPERATURE,MEASURED_TEMPERATURE,
                                        MEASURED_HUMIDITY,STATUS_FAN, STATUS_LIGHT,
                                        MEASURED_MOISTURE_A, MEASURED_MOISTURE_B,
                                        MEASURED_MOISTURE_C)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (values['id'],time,values['sd'],values['ct'],values['mt'],
                    values['mh'],values['sf'],values['sl'],
                    values['mma'],values['mmb'],values['mmc']))
        con.commit()

def save_cfg(request):
    ID = request.form['ID'];
    NAME = request.form['NAME'];
    SLEEP_TIME_SPRINKLE = request.form['SLEEP_TIME_SPRINKLE'];
    TEMPERATURE_THRESHOLD = request.form['TEMPERATURE_THRESHOLD'];
    MASK_CRON_LIGHT_ON = request.form['MASK_CRON_LIGHT_ON'];
    MASK_CRON_LIGHT_OFF = request.form['MASK_CRON_LIGHT_OFF'];
    MASK_CRON_CTRL = request.form['MASK_CRON_CTRL'];

    con = mdb.connect(cfg["db"]["host"], cfg["db"]["user"], cfg["db"]["password"], cfg["db"]["schema"])
    cur = con.cursor()
    try:
        cur.execute("""UPDATE NODE SET NAME=%s, TEMPERATURE_THRESHOLD=%s,
                                            MASK_CRON_LIGHT_ON=%s, MASK_CRON_LIGHT_OFF=%s,
                                            MASK_CRON_CTRL=%s, SLEEP_TIME_SPRINKLE=%s where ID = %s""",
                    (NAME,
                    TEMPERATURE_THRESHOLD,
                    MASK_CRON_LIGHT_ON,
                    MASK_CRON_LIGHT_OFF,
                    MASK_CRON_CTRL,
                    SLEEP_TIME_SPRINKLE,
                    ID))
        con.commit()
        return 0
    except:
        print(e)
        return -1
    finally:
        cur.close()
        con.close()

def save_supplier(request):
    NAME = request.form['nome'];
    TYPE = request.form['tipo'];
    STATE = request.form['estado'];
    CITY = request.form['cidade'];

    con = mdb.connect(cfg["db"]["host"], cfg["db"]["user"], cfg["db"]["password"], cfg["db"]["schema"])
    cur = con.cursor()
    try:
        cur.execute("""INSERT SUPPLIER (NAME,TYPE,STATE,CITY)
                            VALUES(%s,%s,%s,%s)""",
                    (NAME,TYPE,STATE,CITY))
        con.commit()
        return 0
    except:
        print(e)
        return -1
    finally:
        cur.close()
        con.close()

def save_plant(request):
    NAME = request.form['nome'];
    TYPE = request.form['tipo'];
    SUPPLIER = request.form['plant-supplier'];

    con = mdb.connect(cfg["db"]["host"], cfg["db"]["user"], cfg["db"]["password"], cfg["db"]["schema"])
    cur = con.cursor()
    try:
        cur.execute("""INSERT PLANT (NAME,TYPE,SUPPLIER)
                            VALUES(%s,%s,%s)""",
                    (NAME,TYPE,SUPPLIER))
        con.commit()
        return 0
    except:
        return -1
    finally:
        cur.close()
        con.close()

def save_module(request):
    ID = request.form['nome'];
    TYPE = request.form['tipo'];
    OASIS = request.form['oasis'];
    DATE = request.form['data'];

    con = mdb.connect(cfg["db"]["host"], cfg["db"]["user"], cfg["db"]["password"], cfg["db"]["schema"])
    cur = con.cursor()
    try:
        cur.execute("""INSERT MODULE (ID,TYPE,OASIS,DATE)
                            VALUES(%s,%s,%s,%s)""",
                    (ID,TYPE,OASIS,DATE))
        con.commit()
        return 0
    except:
        return -1
    finally:
        cur.close()
        con.close()

def save_crop(request):
    ID = request.form['id'];
    STATE = request.form['estado'];
    CITY = request.form['cidade'];
    DATE = request.form['data'];
    STATUS = request.form['status'];
    con = mdb.connect(cfg["db"]["host"], cfg["db"]["user"], cfg["db"]["password"], cfg["db"]["schema"])
    cur = con.cursor()
    print("ID:"+ID)
    try:
        if ID == "":
            cur.execute("""INSERT CROP (CITY,STATE,START_DATE,STATUS)
                            VALUES(%s,%s,%s,%s)""",
                            (CITY,STATE,DATE,STATUS))
        else:
            cur.execute("""UPDATE CROP SET CITY=%s,STATE=%s,START_DATE=%s,STATUS=%s
                            WHERE ID=CONV(%s,16,10)""",
                            (CITY,STATE,DATE,STATUS,ID))
        #print(cur.lastrowid)
        con.commit()
        return 0
    except:
        return -1
    finally:
        cur.close()
        con.close()

def save_crop_module(request):
    cropDetailId = request.form['cropDetailId'];
    CROP = request.form['cropModuleModalFormId'];
    MODULE = request.form['modulo'];
    PLANT = request.form['planta'];
    SUBSTRATE = request.form['substrato'];
    con = mdb.connect(cfg["db"]["host"], cfg["db"]["user"], cfg["db"]["password"], cfg["db"]["schema"])
    cur = con.cursor()
    try:
        if cropDetailId == "":
            cur.execute("""INSERT CROP_DETAIL (CROP,MODULE,PLANT,SUBSTRATE)
                            VALUES(CONV(%s,16,10),%s,%s,%s)""",
                            (CROP,MODULE,PLANT,SUBSTRATE))
        else:
            cur.execute("""UPDATE CROP_DETAIL SET MODULE=%s,PLANT=%s,SUBSTRATE=%s
                            WHERE ID=%s""",
                            (MODULE,PLANT,SUBSTRATE,cropDetailId))
        #print(cur.lastrowid)
        con.commit()
        return 0
    except:
        return -1
    finally:
        cur.close()
        con.close()

def delete_crop_module(id):
    con = mdb.connect(cfg["db"]["host"], cfg["db"]["user"], cfg["db"]["password"], cfg["db"]["schema"])
    cur = con.cursor()
    try:
        cur.execute("DELETE FROM CROP_DETAIL WHERE ID=%s",(id,))
        con.commit()
        return 0
    except:
        return -1
    finally:
        cur.close()
        con.close()

def retrive_crop_module(id):
    con = mdb.connect(cfg["db"]["host"], cfg["db"]["user"], cfg["db"]["password"], cfg["db"]["schema"])
    with con:
        cur = con.cursor()
        cur.execute("""SELECT CD.ID, CD.MODULE, P.NAME AS PLANT, CD.PLANT AS PLANT_ID, CD.SUBSTRATE
                            FROM CROP_DETAIL CD, PLANT P
                            WHERE CD.PLANT = P.ID AND CROP = CONV(%s,16,10)""", (id,))
        r = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
        return json.dumps(r)

def retrieve_crops():
    con = mdb.connect(cfg["db"]["host"], cfg["db"]["user"], cfg["db"]["password"], cfg["db"]["schema"])
    with con:
        cur = con.cursor()
        cur.execute("SELECT HEX(ID),CITY,STATE,START_DATE,STATUS,COMMENT FROM CROP")
        return cur.fetchall()

def retrieve_modules():
    con = mdb.connect(cfg["db"]["host"], cfg["db"]["user"], cfg["db"]["password"], cfg["db"]["schema"])
    with con:
        cur = con.cursor()
        cur.execute("SELECT M.ID,M.TYPE,N.NAME,M.DATE FROM MODULE M, NODE N WHERE M.OASIS = N.ID")
        return cur.fetchall()

def retrieve_oasis():
    con = mdb.connect(cfg["db"]["host"], cfg["db"]["user"], cfg["db"]["password"], cfg["db"]["schema"])
    with con:
        cur = con.cursor()
        cur.execute("SELECT ID, NAME FROM NODE")
        return cur.fetchall()

def retrieve_plants():
    con = mdb.connect(cfg["db"]["host"], cfg["db"]["user"], cfg["db"]["password"], cfg["db"]["schema"])
    with con:
        cur = con.cursor()
        cur.execute("SELECT P.ID, P.NAME,P.TYPE,S.TYPE, S.NAME FROM PLANT P, SUPPLIER S WHERE P.SUPPLIER = S.ID  ORDER BY P.NAME ASC")
        return cur.fetchall()

def retrieve_suppliers():
    con = mdb.connect(cfg["db"]["host"], cfg["db"]["user"], cfg["db"]["password"], cfg["db"]["schema"])
    with con:
        cur = con.cursor()
        cur.execute("SELECT ID,NAME,TYPE,CITY,STATE FROM SUPPLIER ORDER BY NAME ASC")
        return cur.fetchall()

def retrieve_data(id):
    con = mdb.connect(cfg["db"]["host"], cfg["db"]["user"], cfg["db"]["password"], cfg["db"]["schema"])
    with con:
        cur = con.cursor()
        cur.execute("SELECT TIMESTAMP, MEASURED_TEMPERATURE, MEASURED_HUMIDITY FROM DATA WHERE ID=%s", (id,))
        return cur.fetchall()


def retrieve_all_cfg():
    con = mdb.connect(cfg["db"]["host"], cfg["db"]["user"], cfg["db"]["password"], cfg["db"]["schema"])
    with con:
        cur = con.cursor()
        cur.execute("SELECT * FROM NODE")
        return cur.fetchall()

def retrieve_last_telemetry_info():
    con = mdb.connect(cfg["db"]["host"], cfg["db"]["user"], cfg["db"]["password"], cfg["db"]["schema"])
    with con:
        cur = con.cursor()
        cur.execute("""SELECT   N.NAME,
                                N.ID,
                                N.MODE,
                                D.TIMESTAMP,
                                D.MEASURED_TEMPERATURE,
                                D.MEASURED_HUMIDITY,
                                D.STATUS_FAN,
                                D.STATUS_LIGHT,
                                D.MEASURED_MOISTURE_A,
                                D.MEASURED_MOISTURE_B,
                                D.MEASURED_MOISTURE_C
                            FROM (
	                               SELECT *
                                		FROM (SELECT ID, MAX(TIMESTAMP) AS TIMESTAMP
                                				FROM DATA GROUP BY ID) DM
                                		INNER JOIN DATA DD USING (ID, TIMESTAMP)
                                )D INNER JOIN NODE N USING (ID)""")
        return cur.fetchall()

def syncronize_node_cfg(id, mode):
    con = mdb.connect(cfg["db"]["host"], cfg["db"]["user"], cfg["db"]["password"], cfg["db"]["schema"])
    with con:
        cur = con.cursor()
        cur.execute("""SELECT TEMPERATURE_THRESHOLD,MASK_CRON_LIGHT_ON,
                              MASK_CRON_LIGHT_OFF,MASK_CRON_CTRL,SLEEP_TIME_SPRINKLE
                        FROM NODE WHERE ID = %s""", (id,))
        conf = ""
        for row in cur.fetchall():
            conf = "id:"+id+";temp:"+str(row[0])+";"
            # ask node to reboot because we are sending new crontab parameters
            conf += "mclon:"+str(row[1])+";mcloff:"+str(row[2])+";mcctrl:"+str(row[3])+";"
            conf += "sts:"+str(row[4])+";"
            conf += "cmd:0"
        if mode is None:
            cur.execute("UPDATE NODE SET LAST_UPDATE = %s WHERE ID = %s", (int(time.time()),id))
        else:
            cur.execute("UPDATE NODE SET MODE = %s, LAST_UPDATE = %s WHERE ID = %s", (mode, int(time.time()),id))

        con.commit()
        return conf

def get_node_cfg(id):
    con = mdb.connect(cfg["db"]["host"], cfg["db"]["user"], cfg["db"]["password"], cfg["db"]["schema"])
    with con:
        cur = con.cursor()
        cur.execute("""SELECT NAME,
                              TEMPERATURE_THRESHOLD,
                              MASK_CRON_LIGHT_ON,
                              MASK_CRON_LIGHT_OFF,
                              MASK_CRON_CTRL,
                              SLEEP_TIME_SPRINKLE
                        FROM NODE WHERE ID = %s""", (id,))
        return cur.fetchone()
