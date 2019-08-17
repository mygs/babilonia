#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import time
import json
import datetime as dt
import logging
import logging.config
from Models import *
#import analytics
import simplejson as json
from flask import Flask, render_template, request
from flask_mqtt import Mqtt
from flask_socketio import SocketIO
from flask_assets import Environment, Bundle
from croniter import croniter
#from flask_qrcode import QRcode
from sqlalchemy import func, and_

###############################################################################
#################### CONFIGURATION AND INITIALISATION #########################
###############################################################################
###### create console handler and set level to debug
project_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(project_dir, 'logging.json'), "r") as logging_json_file:
    logging_config = json.load(logging_json_file)
    log_dir = project_dir+"/../log"
    if os.path.exists(log_dir) == False:
        os.makedirs(log_dir)
    logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)

###### reading configuration
with open(os.path.join(project_dir, 'config.json'), "r") as config_json_file:
    cfg = json.load(config_json_file)
isMQTTenabled = cfg["MODE"]["MQTT"]
###### Initialisation
app = Flask(__name__, static_url_path='/static')

app.config['MQTT_BROKER_URL'] = cfg["MQTT"]["BROKER"]
app.config['MQTT_BROKER_PORT'] = cfg["MQTT"]["PORT"]
app.config['MQTT_KEEPALIVE'] = cfg["MQTT"]["KEEPALIVE"]
app.config['SQLALCHEMY_DATABASE_URI'] = cfg["SQLALCHEMY_DATABASE_URI"]
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

if isMQTTenabled:
    mqtt = Mqtt(app)

DB.init_app(app)

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


###############################################################################
############################# MANAGE WEB REQ/RESP #############################
###############################################################################

@app.route('/')
def index():
    with app.app_context():
        time_start = time.time()
        latest = DB.session.query(OasisData.NODE_ID,
            func.max(OasisData.TIMESTAMP).label('TIMESTAMP')).group_by(OasisData.NODE_ID).subquery('t2')
        modules = DB.session.query(OasisData).join(
            latest, and_(OasisData.NODE_ID == latest.c.NODE_ID,OasisData.TIMESTAMP == latest.c.TIMESTAMP))
        time_end = time.time()
        delta= time_end - time_start
        logger.debug("[database] call database for index page took %s secs",time.strftime("%S", time.gmtime(delta)))

        return render_template('index.html', modules=modules)

@app.route('/status', methods=['POST'])
def refresh():
    message = json.dumps(request.get_json())
    logger.debug("[status] %s", message)
    if isMQTTenabled:
        mqtt.publish("/oasis-inbound", message)
    return json.dumps({'status':'Success!'});

@app.route('/command', methods=['POST'])
def command():
    message = json.dumps(request.get_json())
    logger.debug("[command] %s", message)
    if isMQTTenabled:
        mqtt.publish("/oasis-inbound", message)
    return json.dumps({'status':'Success!'});

@app.route('/about')
def about():
    return render_template('about.html')


###############################################################################
################################# PROCESSORS ##################################
###############################################################################

@app.context_processor
def utility_processor():
    def format_last_update(value):
        return time.strftime("%d/%m/%Y %H:%M:%S", time.localtime(int(value)))
    def status_node(last_update, sensor_collect_data_period):
        last_update = int(last_update)
        sensor_collect_data_period = int(sensor_collect_data_period)
        now = int(time.time())
        next_data_is_expected = last_update + sensor_collect_data_period
        if next_data_is_expected >= now: # NEXT is future
            return "good"
        else:
            return "danger"
    return {
            'status_node':status_node,
            'format_last_update':format_last_update
            }
###############################################################################
############################## HANDLE MQTT ####################################
###############################################################################

if cfg["MODE"]["MQTT"] == True:
# The callback for when the client receives a CONNACK response from the server.
    @mqtt.on_connect()
    def handle_mqtt_connect(client, userdata, flags, rc):
        logger.debug("Connected with result code %s",str(rc))
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        mqtt.subscribe(cfg["MQTT"]["MQTT_OASIS_TOPIC_HEARTBEAT"])
        mqtt.subscribe(cfg["MQTT"]["MQTT_OASIS_TOPIC_OUTBOUND"])

    # The callback for when a PUBLISH message is received from the server.
    @mqtt.on_message()
    def handle_mqtt_message(client, userdata, msg):
        topic = msg.topic
        jmsg = json.loads(msg.payload)
        node_id = jmsg["NODE_ID"]
        timestamp = int(time.time())

        if topic == cfg["MQTT"]["MQTT_OASIS_TOPIC_HEARTBEAT"]:
            logger.debug("[heartbeat] from %s", jmsg["NODE_ID"])
            heartbeat = OasisHeartbeat(NODE_ID=node_id,LAST_UPDATE=timestamp)
            with app.app_context():
                DB.session.merge(heartbeat)
        if topic == cfg["MQTT"]["MQTT_OASIS_TOPIC_OUTBOUND"]:
            logger.debug("[data] from %s at %s", jmsg["NODE_ID"], jmsg)
            data = OasisData(TIMESTAMP=timestamp,NODE_ID=node_id,DATA=jmsg)
            with app.app_context():
                DB.session.add(data)


###############################################################################
##################################  START #####################################
###############################################################################

if __name__ == '__main__':
    print("")
    print("    __            __     _  __               _       ")
    print("   / /_   ____ _ / /_   (_)/ /____   ____   (_)____ _")
    print("  / __ \ / __ `// __ \ / // // __ \ / __ \ / // __ `/")
    print(" / /_/ // /_/ // /_/ // // // /_/ // / / // // /_/ / ")
    print("/_.___/ \__,_//_.___//_//_/ \____//_/ /_//_/ \__,_/  ")
    print("")
    print("*** STARTING NABUCODONOSOR SYSTEM ***")
    user_reload = True
    if isMQTTenabled:
        user_reload = False # Avoid Bug: TWICE mqtt instances
    socketio.run(app, host='0.0.0.0', port=8181, debug=True, use_reloader=user_reload)
