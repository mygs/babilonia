#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import time
import subprocess
import git
import json
import datetime as dt
import logging
import logging.config
from Models import *
#import analytics
import simplejson as json
import requests
from flask import Flask, Response, url_for, redirect, render_template, request, session, abort
from flask_mqtt import Mqtt
from flask_socketio import SocketIO
from flask_assets import Environment, Bundle
#from croniter import croniter
#from flask_qrcode import QRcode
from sqlalchemy import func, and_
from flask_login import LoginManager, login_required, login_user, logout_user



###############################################################################
#################### CONFIGURATION AND INITIALISATION #########################
###############################################################################
###### create console handler and set level to debug
SERVER_HOME = os.path.dirname(os.path.abspath(__file__))
LOG_DIR=os.path.join(SERVER_HOME, '../log')
COMMON_DIR=os.path.join(SERVER_HOME, '../../common')
os.chdir(SERVER_HOME) #change directory because of log files
with open(os.path.join(SERVER_HOME, 'logging.json'), "r") as logging_json_file:
    logging_config = json.load(logging_json_file)
    if os.path.exists(LOG_DIR) == False:
        os.makedirs(LOG_DIR)
    logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)
###### reading version
VERSION = subprocess.check_output(["git", "describe", "--tags","--always"],
                                cwd=SERVER_HOME).strip()
###### reading configuration
with open(os.path.join(SERVER_HOME, 'config.json'), "r") as config_json_file:
    cfg = json.load(config_json_file)
isMQTTDataRecordEnabled = cfg["MODE"]["MQTT"]

###### Initialisation
app = Flask(__name__, static_url_path='/static')
app.config['MQTT_BROKER_URL'] = cfg["MQTT"]["BROKER"]
app.config['MQTT_BROKER_PORT'] = cfg["MQTT"]["PORT"]
app.config['MQTT_KEEPALIVE'] = cfg["MQTT"]["KEEPALIVE"]
app.config['SQLALCHEMY_DATABASE_URI'] = cfg["SQLALCHEMY_DATABASE_URI"]
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = cfg["SECRET_KEY"]
app.config['LOGIN_DISABLED'] = cfg["LOGIN_DISABLED"]

NODE_HOME=os.path.join(os.environ["BABILONIA_HOME"], 'node/ino')
ESPMAKE_PARAM=os.path.join(os.environ["BABILONIA_LIBS"], 'makeEspArduino/makeEspArduino.mk')

logger.info("BABILONIA_HOME: %s",os.environ["BABILONIA_HOME"])
logger.info("BABILONIA_LIBS: %s",os.environ["BABILONIA_LIBS"])
logger.info("NODE_HOME: %s",NODE_HOME)

mqtt = Mqtt(app)
DB.init_app(app)
socketio = SocketIO(app)
assets = Environment(app)
login_manager = LoginManager()
login_manager.init_app(app)
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

def update_server_software():
    repo = git.Repo(os.environ["BABILONIA_HOME"])
    repo.remotes.origin.pull()
    subprocess.check_output(["sudo", "service", "nabucodonosor", "restart"])
###############################################################################
############################# MANAGE WEB REQ/RESP #############################
###############################################################################
@login_manager.user_loader
def load_user(username):
    return User.query.get(username)

# somewhere to login
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        registered_user = User.query.filter_by(USERNAME=username,PASSWORD=password).first()

        if registered_user is None:
            logger.warn("[Invalid Credential] username: %s password: %s",username, password)
            error = 'Invalid Credentials. Please try again.'
        else:
            login_user(registered_user)
            return redirect('/')
    return render_template('login.html', error=error)


# somewhere to logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/login')

# handle page not found
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
# handle login failed
@app.errorhandler(401)
def page_not_found(e):
    return redirect('/login')

@app.route('/')
@login_required
def index():
    weather = weather_currently()
    return render_template('index.html', weather=weather)

def weather_currently():
    weather_key = cfg["WEATHER_KEY"]
    lat = cfg["LATITUDE"]
    long = cfg["LONGITUDE"]
    response = requests.get('https://api.forecast.io/forecast/%s/%s,%s?units=si&lang=pt&exclude=flags,hourly,daily'%(
                                weather_key, lat, long))
    data = response.json()
    logger.debug("[weather] %s", data)
    return data['currently']

@app.route('/module')
@login_required
def module():
    with app.app_context():
        time_start = dt.datetime.now()
        latest = DB.session.query(OasisData.NODE_ID,
            func.max(OasisData.TIMESTAMP).label('TIMESTAMP')).filter(
            OasisData.DATA['DATA']['NODE'].isnot(None)).group_by(
            OasisData.NODE_ID).subquery('t2')
        modules = DB.session.query(OasisData).join(
            latest, and_(OasisData.NODE_ID == latest.c.NODE_ID,OasisData.TIMESTAMP == latest.c.TIMESTAMP))
        time_end = dt.datetime.now()
        elapsedTime = time_end - time_start
        logger.debug("[database] call database for index page took %s secs",elapsedTime.total_seconds())

        return render_template('module.html', modules=modules)


@app.route('/configuration', methods=['POST'])
@login_required
def node_config():
    id = request.form['id'];
    logger.debug("[configuration] getting config for %s", id)
    #TODO: merge with current config
    #node = database.get_node_cfg(id);
    DEFAULT_CONFIG_FILE = os.path.join(COMMON_DIR, 'config/oasis.json')
    with open(DEFAULT_CONFIG_FILE, "r") as default_config:
        config = json.load(default_config)
    return json.dumps(config);

@app.route('/status', methods=['POST'])
@login_required
def refresh():
    message = json.dumps(request.get_json())
    logger.debug("[status] %s", message)
    mqtt.publish("/oasis-inbound", message)
    return json.dumps({'status':'Success!'});

@app.route('/command', methods=['POST'])
@login_required
def command():
    message = json.dumps(request.get_json())
    logger.debug("[command] %s", message)
    mqtt.publish("/oasis-inbound", message)
    return json.dumps({'status':'Success!'});


@app.route("/firmware")
@login_required
def firmware():
    with app.app_context():
        time_start = dt.datetime.now()
        latest = DB.session.query(OasisData.NODE_ID,
            func.max(OasisData.TIMESTAMP).label('TIMESTAMP')).group_by(OasisData.NODE_ID).subquery('t2')
        modules = DB.session.query(OasisData).join(
            latest, and_(OasisData.NODE_ID == latest.c.NODE_ID,OasisData.TIMESTAMP == latest.c.TIMESTAMP))
        time_end = dt.datetime.now()
        elapsedTime = time_end - time_start
        logger.debug("[database] call database for firware page took %s secs",elapsedTime.total_seconds())

        return render_template('firmware/firmware.html', modules=modules)

@app.route('/progress')
@login_required
def progress():
    logger.info("[firmware] env: %s",os.environ)
    #clean
    logger.info("[firmware] cleaning arduino firmware")
    clean_output=subprocess.check_output(["make","-f", ESPMAKE_PARAM, "clean"],
                                            cwd=NODE_HOME)
    logger.info("[firmware] %s", clean_output)
    #build
    logger.info("[firmware] building new arduino firmware")
    build_output = subprocess.Popen(["make","-f",ESPMAKE_PARAM],
                                        cwd=NODE_HOME,
                                        stdout=subprocess.PIPE)
    def generate():
        x = 0
        while x <= 100:
            line = build_output.stdout.readline()
            yield "data:" + str(x) + "\n\n"
            logger.info("[firmware] progress %i: %s",x,line.rstrip())
            x = x + 1
    return Response(generate(), mimetype= 'text/event-stream')


@app.route('/about')
@login_required
def about():
    return render_template('about.html')

@app.route('/webhook', methods=['POST'])
def webhook():
    message = request.get_json()

    if message is not None:
        logger.info("[webhook] message:%s",message)
        committer = message["pusher"]["name"]
        commit_message = message["head_commit"]["message"]

        logger.info("[webhook] commit:%s author:%s",commit_message, committer)
        if cfg["MODE"]["AUTO_UPDATE_SERVER"] == True:
            logger.info("[webhook] applying update")
            update_server_software()
        else:
            logger.warn("[webhook] auto updates not applied")

        return json.dumps({'status':'request!'});

    return json.dumps({'status':'request was ignored!'});

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
    def status_moisture(hasMoisture, id, mux):
        moisture = int(mux)
        if not hasMoisture or mux < 50:
            return "moisture-disable"
        else:
            #TODO: put some brain in here
            return "moisture-wet"
    def weather_icon(argument):
        switcher = {
            "clear-day": "wi wi-day-sunny",
            "clear-night": "wi wi-night-clear",
            "rain": "wi wi-rain",
            "snow": "wi wi-snow",
            "sleet": "wi wi-sleet",
            "wind": "wi wi-wind",
            "fog": "wi wi-fog",
            "cloudy": "wi wi-cloudy",
            "partly-cloudy-day": "wi wi-forecast-io-partly-cloudy-day",
            "partly-cloudy-night": "wi wi-forecast-io-partly-cloudy-day"
        }
        return switcher.get(argument, "wi wi-day-sunny")
    return {
            'status_node':status_node,
            'status_moisture':status_moisture,
            'weather_icon': weather_icon,
            'format_last_update':format_last_update
            }
###############################################################################
############################## HANDLE MQTT ####################################
###############################################################################

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
        heartbeat = OasisHeartbeat(NODE_ID=node_id,LAST_UPDATE=timestamp)
        logger.debug("[heartbeat] %s", heartbeat.toJson())
        socketio.emit('ws-oasis-heartbeat', data=heartbeat.toJson())
        if isMQTTDataRecordEnabled:
            with app.app_context():
                DB.session.merge(heartbeat)
    if topic == cfg["MQTT"]["MQTT_OASIS_TOPIC_OUTBOUND"]:
        data = OasisData(TIMESTAMP=timestamp,NODE_ID=node_id,DATA=jmsg)
        logger.debug("[data] %s", data.toJson())
        socketio.emit('ws-oasis-data', data=data.toJson())
        if isMQTTDataRecordEnabled and "DATA" in jmsg:
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
    logger.info("*** STARTING NABUCODONOSOR SYSTEM ***")
    logger.info("version: %s", VERSION)

    user_reload = False # Avoid Bug: TWICE mqtt instances
    socketio.run(app, host='0.0.0.0', port=8181, debug=True, use_reloader=user_reload)
