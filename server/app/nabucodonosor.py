#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import time
import datetime as dt
import logging
import logging.config
import database
#import analytics
import simplejson as json
from flask import Flask, render_template, request
from flask_mqtt import Mqtt
from flask_socketio import SocketIO
from flask_assets import Environment, Bundle
from croniter import croniter
#from flask_qrcode import QRcode

###############################################################################
#################### CONFIGURATION AND INITIALISATION #########################
###############################################################################
###### create console handler and set level to debug
project_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(project_dir, 'logging.json'), "r") as logging_json_file:
    logging_config = json.load(logging_json_file)
    os.makedirs(project_dir+"/../log",exist_ok=True)
    logging.config.dictConfig(logging_config)
logger = logging.getLogger()

###### reading configuration
project_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(project_dir, 'config.json'), "r") as config_json_file:
    cfg = json.load(config_json_file)

###### Initialisation
app = Flask(__name__, static_url_path='/static')

app.config['MQTT_BROKER_URL'] = cfg["MQTT"]["BROKER"]
app.config['MQTT_BROKER_PORT'] = cfg["MQTT"]["PORT"]
app.config['MQTT_KEEPALIVE'] = cfg["MQTT"]["KEEPALIVE"]

app.config['MYSQL_DATABASE_USER'] =  cfg["DATABASE"]["USER"]
app.config['MYSQL_DATABASE_PASSWORD'] =  cfg["DATABASE"]["PASSWORD"]
app.config['MYSQL_DATABASE_DB'] = cfg["DATABASE"]["SCHEMA"]
app.config['MYSQL_DATABASE_HOST'] = cfg["DATABASE"]["HOST"]

if cfg["MODE"]["MQTT"] == True:
    mqtt = Mqtt(app)

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

@app.route('/about')
def about():
    return render_template('about.html')


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
        timestamp = int(time.time())

        if topic == cfg["MQTT"]["MQTT_OASIS_TOPIC_HEARTBEAT"]:
            logger.debug("[heartbeat] from %s", jmsg["NODE_ID"])
            database.update_oasis_heartbeat(jmsg["NODE_ID"], timestamp)
        if topic == cfg["MQTT"]["MQTT_OASIS_TOPIC_OUTBOUND"]:
            logger.debug("[data] from %s at %s", jmsg["NODE_ID"], jmsg)


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
    if cfg["MODE"]["MQTT"] == True:
        user_reload = False # Avoid Bug: TWICE mqtt instances
    socketio.run(app, host='0.0.0.0', port=8181, debug=True, use_reloader=user_reload)
