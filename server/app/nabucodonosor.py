#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import time
import datetime as dt
import logging
import logging.config
import database
import analytics
import simplejson as json
from flask import Flask, render_template, request
from flaskext.mysql import MySQL
from flask_mqtt import Mqtt
from flask_socketio import SocketIO
from flask_assets import Environment, Bundle
from croniter import croniter
#from flask_qrcode import QRcode

project_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(project_dir, 'config.json'), "r") as json_data_file:
    cfg = json.load(json_data_file)

# create console handler and set level to debug
project_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(project_dir, 'logging.json'), "r") as fd:
    logging.config.dictConfig(json.load(fd))
logger = logging.getLogger()

mysql = MySQL()
app = Flask(__name__, static_url_path='/static')

app.config['MQTT_BROKER_URL'] = cfg["mqtt"]["broker"]
app.config['MQTT_BROKER_PORT'] = cfg["mqtt"]["port"]
app.config['MQTT_KEEPALIVE'] = cfg["mqtt"]["keepalive"]

app.config['MYSQL_DATABASE_USER'] =  cfg["db"]["user"]
app.config['MYSQL_DATABASE_PASSWORD'] =  cfg["db"]["password"]
app.config['MYSQL_DATABASE_DB'] = cfg["db"]["schema"]
app.config['MYSQL_DATABASE_HOST'] = cfg["db"]["host"]

if cfg["mode"]["mqtt"] == True:
    mqtt = Mqtt(app)

mysql.init_app(app)
socketio = SocketIO(app)
assets = Environment(app)
#qrcode = QRcode(app)


assets.load_path = [os.path.join(os.path.dirname(__file__), 'static/fonts'),
                    os.path.join(os.path.dirname(__file__), 'static')]
assets.register('3rdpartycss',
                'css/3rdparty/bootstrap.css',
                'css/3rdparty/dataTables.bootstrap.css',
                'css/3rdparty/buttons.bootstrap.css',
                'css/3rdparty/select.bootstrap.css',
                'css/3rdparty/sticky-footer-navbar.css',
                'css/3rdparty/font-awesome.css',
                'css/3rdparty/weather-icons.css',
                'css/3rdparty/sweetalert.css',
                'css/3rdparty/bootstrap-datepicker.css',
                output='assets/3rdparty.css',
                filters='cssmin')

assets.register('3rdpartyjs',
                'js/3rdparty/jquery-2.2.4.js',
                'js/3rdparty/jquery-ui.js',
                'js/3rdparty/jquery.dataTables.js',
                'js/3rdparty/dataTables.bootstrap.js',
                'js/3rdparty/dataTables.buttons.js',
                'js/3rdparty/buttons.bootstrap.js',
                'js/3rdparty/bootstrap-datepicker.js',
                'js/3rdparty/dataTables.select.js',
                'js/3rdparty/bootstrap.js',
                'js/3rdparty/socket.io.js',
                'js/3rdparty/moment.js',
                'js/3rdparty/sweetalert.min.js',
                'js/3rdparty/Chart.js',
                output='assets/3rdparty.js',
                filters='jsmin')

@app.route('/')
def index():
    modules = database.retrieve_last_telemetry_info();
    return render_template('index.html', modules=modules)

@app.route('/test')
def test():
    return render_template('test.html')

@app.route('/timeseries', methods=['POST'])
def timeseries():
    id = request.form['id'];
    return analytics.get_timeseries(id);

@app.route('/configuration', methods=['POST'])
def node():
    id = request.form['id'];
    node = database.get_node_cfg(id);
    if node is None:
        return json.dumps({ 'TEMPERATURE_THRESHOLD':cfg["defaults"]["TEMPERATURE_THRESHOLD"],
                            'MASK_CRON_LIGHT_ON':cfg["defaults"]["MASK_CRON_LIGHT_ON"],
                            'MASK_CRON_LIGHT_OFF':cfg["defaults"]["MASK_CRON_LIGHT_OFF"],
                            'MASK_CRON_CTRL':cfg["defaults"]["MASK_CRON_CTRL"],
                            'SLEEP_TIME_SPRINKLE':cfg["defaults"]["SLEEP_TIME_SPRINKLE"]});
    else:
        return json.dumps({ 'NAME':node[0],
                            'MODE':node[1],
                            'TEMPERATURE_THRESHOLD':node[2],
                            'MASK_CRON_LIGHT_ON':node[3],
                            'MASK_CRON_LIGHT_OFF':node[4],
                            'MASK_CRON_CTRL':node[5],
                            'SLEEP_TIME_SPRINKLE':node[6]});

@app.route('/updatecfg', methods=['POST'])
def updatecfg():
    status = database.save_cfg(request);
    conf = database.syncronize_node_cfg(request.form['ID'], None)
    if cfg["mode"]["mqtt"] == True:
        mqtt.publish("/cfg", conf)
    if status == 0:
        return  json.dumps({ 'status': status, 'message':'Configuração foi gravado com sucesso'});
    else:
        return json.dumps({ 'status':status, 'message':'Configuração não foi gravado'});

@app.route('/deletenode', methods=['POST'])
def deletenode():
    status = database.delete_node(request.form['ID']);
    if status == 0:
        return  json.dumps({ 'status': status, 'message':'Node removido com sucesso'});
    else:
        return json.dumps({ 'status':status, 'message':'Fail to remove node'});

@app.route('/command', methods=['POST'])
def command():
    id = request.form['id'];
    command = request.form['command'];
    param = request.form['param'];
    if cfg["mode"]["mqtt"] == True:
        mqtt.publish("/cfg", "id:{};{}:{}".format(id, command, param))
    return json.dumps({'status':'Success!'});

@app.context_processor
def utility_processor():
    def status_node(timestamp, node_id):
        node = database.get_node_cfg(node_id);
        MASK_CRON_CTRL = node[5];
        NEXT = croniter(MASK_CRON_CTRL, int(timestamp)).get_next()
        NOW = int(time.time())
        DELTA = NEXT - NOW
        if DELTA > 0: # NEXT is future
            return "good"
        if DELTA > -60: # 1 min delayed
            return "nostatus"
        else:
            return "danger"
    def mode(mode):
        if mode is None or mode=="":
            return "undefinedmode"
        if int(mode) == 0:
            return "indoor"
        elif int(mode) == 1:
            return "outdoor"
        else: # Not Define Yet
            return "undefinedmode"
    def disableBtn(btn, mode):
        if mode is None or mode=="":
            return ""
        if int(mode) == 1 and btn != "sop": #outdoor => disable fan and light
            return "disabled=disable"
        elif int(mode) == 0 and btn == "sop": #indoor => disable sop
            return "disabled=disable"
        else:
            return ""
    def format_timestamp(value):
        return time.strftime("%d/%m/%Y %H:%M:%S", time.localtime(int(value)))
    def format_temperature(value):
        return u'{0:2.0f}°C'.format(value)
    def format_humidity(value):
        return u'{0:.2f}%'.format(value)
    def format_moisture(value, mode):
        if mode is None or mode=="" or int(mode) == 0:
            return 'N/A'
        if int(value) == 1:
            return 'SECO' #DRY: GPIO = 1 / BUILD IN LED = OFF
        else:
            return 'MOLHADO' #WET: GPIO = 0 / BUILD IN LED = ON
    def status(value, mode):
        if mode  is None or mode=="" or int(mode) == 1:
            return 'N/A'
        if int(value) == 1:
            return 'on'
        else:
            return 'off'
    def crop_duration(date, status):
        now = dt.date.today()
        delta = now - date
        if delta.days < 0 or status == 'Planejado' or status == 'Encerrado':
            return ""
        else:
            return str(delta.days)
    return {'format_timestamp':format_timestamp,
            'disableBtn':disableBtn,
            'format_temperature':format_temperature,
            'format_humidity':format_humidity,
            'format_moisture':format_moisture,
            'status':status,
            'status_node':status_node,
            'mode':mode,
            'crop_duration':crop_duration
            }


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/management')
def management():
    crops = database.retrieve_crops()
    modules = database.retrieve_modules()
    plants = database.retrieve_plants()
    return render_template('management/management.html', crops=crops, modules=modules, plants=plants)

@app.route('/management/save-crop', methods=['POST'])
def savecrop():
    status = database.save_crop(request);
    if status == 0:
        return  json.dumps({ 'status': status, 'message':'Produção foi gravado com sucesso'});
    else:
        return json.dumps({ 'status':status, 'message':'Produção não foi gravado'});

@app.route('/management/crop-module', methods=['GET'])
def cropmodule():
    id = request.args.get('id');
    return database.retrive_crop_module(id)


@app.route('/management/save-crop-module', methods=['POST'])
def savecropmodule():
    status = database.save_crop_module(request);
    if status == 0:
        return  json.dumps({ 'status': status, 'message':'Módulo foi gravado com sucesso'});
    else:
        return json.dumps({ 'status':status, 'message':'Módulo não foi gravado'});

@app.route('/management/delete-crop-module', methods=['POST'])
def deletecropmodule():
    id = request.form['id'];
    status = database.delete_crop_module(id);
    if status == 0:
        return  json.dumps({ 'status': status, 'message':'Módulo foi removido com sucesso'});
    else:
        return json.dumps({ 'status':status, 'message':'Módulo não foi removido'});

@app.route('/management/module')
def module():
    modules = database.retrieve_modules()
    oasis = database.retrieve_oasis()
    return render_template('management/module.html', modules=modules , oasis=oasis)

@app.route('/management/save-module', methods=['POST'])
def savemodule():
    status = database.save_module(request);
    if status == 0:
        return  json.dumps({ 'status': status, 'message':'Módulo foi gravado com sucesso'});
    else:
        return json.dumps({ 'status':status, 'message':'Módulo não foi gravado'});


@app.route('/management/plant')
def plant():
    plants = database.retrieve_plants()
    suppliers = database.retrieve_suppliers()
    return render_template('management/plant.html', plants=plants , suppliers=suppliers)

@app.route('/management/save-plant', methods=['POST'])
def saveplant():
    status = database.save_plant(request);
    if status == 0:
        return  json.dumps({ 'status': status, 'message':'Planta foi gravado com sucesso'});
    else:
        return json.dumps({ 'status':status, 'message':'Planta não foi gravado'});

@app.route('/management/plant-supplier')
def plant_supplier():
    suppliers = database.retrieve_suppliers()
    return render_template('management/plant-supplier.html', suppliers=suppliers)

@app.route('/management/save-plant-supplier', methods=['POST'])
def savesupplier():
    status = database.save_supplier(request);
    if status == 0:
        return  json.dumps({ 'status': status, 'message':'Fornecedor foi gravado com sucesso'});
    else:
        return json.dumps({ 'status':status, 'message':'Fornecedor não foi gravado'});

if cfg["mode"]["mqtt"] == True:
# The callback for when the client receives a CONNACK response from the server.
    @mqtt.on_connect()
    def handle_mqtt_connect(client, userdata, flags, rc):
        logger.info("Connected with result code %s",str(rc))
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        mqtt.subscribe("/online")
        mqtt.subscribe("/data")
        mqtt.subscribe("/cmd-ack")

    # The callback for when a PUBLISH message is received from the server.
    @mqtt.on_message()
    def handle_mqtt_message(client, userdata, msg):
        topic = msg.topic
        data = str(msg.payload, 'utf-8')
        values = dict(item.split(":") for item in data.split(";"))
        logger.info("Receive message on topic %s", topic)

        if topic == "/data":
            timestamp = int(time.time())
            values['timestamp']=timestamp
            socketio.emit('mqtt_message', data=values)
            database.insert_data(timestamp, values)
        if topic == "/cmd-ack":
            timestamp = int(time.time())
            values['timestamp']=timestamp
            socketio.emit('mqtt_message', data=values)
        if topic == "/online":
            if values['rb'] == "0" : # not remote requested boot
                conf = database.syncronize_node_cfg(values['id'],values['mode'])
                if conf != "":
                    mqtt.publish("/cfg", conf)
                else:
                    socketio.emit('alert', data=values)
        if topic == "/moisture":
            timestamp = int(time.time())
            values['timestamp']=timestamp
            socketio.emit('moisture', data=values)
            #database.insert_data(timestamp, values)

if __name__ == '__main__':
    print("*** STARTING NABUCODONOSOR SYSTEM ***")
    user_reload = True
    if cfg["mode"]["mqtt"] == True:
        user_reload = False # Avoid Bug: TWICE mqtt instances
    socketio.run(app, host='0.0.0.0', port=8181, debug=True, use_reloader=user_reload)
