#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import sys
import time
import subprocess
import json
import datetime as dt
import logging
import logging.config
import git
from functools import wraps
from Models import *
sys.path.insert(1,os.path.join(os.environ["BABILONIA_LIBS"], 'matricis/SmartIrrigation'))
from SoilMoistureAnalytics import *
from Dashboard import *
from WaterTankManager import *
from Irrigation import *
import simplejson as json
import requests
from flask import Flask, make_response, Response, url_for, redirect, render_template, request, session, abort
from flask_mqtt import Mqtt
from flask_socketio import SocketIO
from flask_assets import Environment, Bundle
#from croniter import croniter
#from flask_qrcode import QRcode
from sqlalchemy import func, and_
from flask_login import LoginManager, login_required, login_user, logout_user
from flask_caching import Cache
from threading import Thread
#from flask_executor import Executor
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from about import about_system
from management import management
from monitor import monitor

###############################################################################
#################### CONFIGURATION AND INITIALISATION #########################
###############################################################################
QUARANTINE_CACHE = {}

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
isMqttEnabled = cfg["MODE"]["MQTT"]
isWebEnabled = cfg["MODE"]["WEB"]

OASIS_PROP_FILE = os.path.join(COMMON_DIR, 'oasis_properties.json')
with open(OASIS_PROP_FILE, "r") as oasis_prop_file:
    oasis_properties = json.load(oasis_prop_file)

OASIS_VOICE_FILE = os.path.join(COMMON_DIR, 'voice_words.json')
with open(OASIS_VOICE_FILE, "r") as voice_words_file:
    voice_words = json.load(voice_words_file)
###### Server GPIO setup
#
# o V G o X Y o o o o o o o o o o o o o o
# o o o o o o o o o o o o o o o o o o o o
#
wtm = WaterTankManager(logger, cfg)
wtm.monitorTankLevel()

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

cache = Cache(config=cfg['CACHE'])
cache.init_app(app)
#executor = Executor(app)

mqtt = Mqtt(app)
DB.init_app(app)
dashboard = Dashboard(logger, cfg)
analytics = SoilMoistureAnalytics(logger, cfg, oasis_properties)
socketio = SocketIO(app)
assets = Environment(app)
login_manager = LoginManager()
login_manager.init_app(app)
#qrcode = QRcode(app)

if cfg["TELEGRAM"]["ENABLE"]:
    from VoiceAssistant import *
    logger.info("[VOICE_ASSISTANT] enabled")
    voiceBot = VoiceAssistant(logger, cfg, oasis_properties, voice_words)
    voiceBot.start()
else:
    logger.info("[VOICE_ASSISTANT] disabled")

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
                'css/3rdparty/bootstrap-switch.min.css',
                output='assets/3rdparty.css',
                filters='cssmin')

assets.register('3rdpartyjs',
                'js/3rdparty/jquery-2.2.4.js',
                'js/3rdparty/js.cookie.js',
                'js/3rdparty/jquery-ui.js',
                'js/3rdparty/jquery.dataTables.js',
                'js/3rdparty/dataTables.bootstrap.js',
                'js/3rdparty/dataTables.buttons.js',
                'js/3rdparty/buttons.bootstrap.js',
                'js/3rdparty/bootstrap-switch.min.js',
                'js/3rdparty/bootstrap-datepicker.js',
                'js/3rdparty/dataTables.select.js',
                'js/3rdparty/popper.min.js',
                'js/3rdparty/bootstrap.js',
                'js/3rdparty/socket.io.min.js',
                'js/3rdparty/moment.js',
                'js/3rdparty/sweetalert.min.js',
#                'js/3rdparty/Chart.js',
                output='assets/3rdparty.js',
                filters='jsmin')

def update_server_software():
    repo = git.Repo(os.environ["BABILONIA_HOME"])
    logger.info("[update_server_software] ignoring local changes")
    repo.git.reset('--hard')
    logger.info("[update_server_software] geting updates")
    repo.remotes.origin.pull()
    logger.info("[update_server_software] restarting the service")
    subprocess.check_output(["sudo", "service", "nabucodonosor", "restart"])
###############################################################################
############################# MANAGE WEB REQ/RESP #############################
###############################################################################
def check_if_gui_is_enable(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not isWebEnabled:
            return render_template('misc/disabled.html')
        return f(*args, **kwargs)
    return decorated_function

@login_manager.user_loader
def load_user(username):
    return User.query.get(username)

# somewhere to login
@app.route("/login", methods=["GET", "POST"])
@check_if_gui_is_enable
def login():
    logger.info("[CLIENT IP] %s", request.remote_addr)
    error = None

    if cfg["FREE_PASS"]["ACTIVE"] and request.remote_addr in cfg["FREE_PASS"]["IP"]:
        logger.info("[Free pass] %s", request.remote_addr)
        free_pass_user = User(cfg["FREE_PASS"]["LOGIN"])
        login_user(free_pass_user)
        return redirect('/')
    else:
        logger.info("[Free pass] disabled")

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        registered_user = User.query.filter_by(USERNAME=username,PASSWORD=password).first()
        print(registered_user)

        if registered_user is None:
            logger.warning("[Invalid Credential] username: %s password: %s",username, password)
            error = 'Invalid Credentials. Please try again.'
        elif registered_user.USERNAME == cfg["FREE_PASS"]["LOGIN"]:
            logger.warning("[Invalid Credential] someone else trying to use free pass user")
            error = 'Invalid Credentials. Please try again.'
        else:
            login_user(registered_user, remember=True)
            browser = request.headers.get('User-Agent')
            if "Lynx" in browser:
                return redirect('/about')
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
    return render_template('misc/404.html'), 404
# handle login failed
@app.errorhandler(401)
def redirect_to_login_page(e):
    return redirect('/login')


def update_quarantine_cache():
    with app.app_context():
        QUARANTINE_CACHE.clear()
        heartbeats = DB.session.query(OasisHeartbeat.NODE_ID, OasisHeartbeat.QUARANTINE).all()

    for hb in heartbeats:
        QUARANTINE_CACHE[hb.NODE_ID] = hb.QUARANTINE
        logger.debug("[update_quarantine_cache] %s is %i", hb.NODE_ID, hb.QUARANTINE)


def get_modules_data(id):
    with app.app_context():
        time_start = dt.datetime.now()
        if id is None:
            latest = DB.session.query(OasisData.NODE_ID,
                func.max(OasisData.TIMESTAMP).label('TIMESTAMP')).group_by(
                OasisData.NODE_ID).subquery('t2')
            modules = DB.session.query(OasisData).join(
                latest, and_(OasisData.NODE_ID == latest.c.NODE_ID,OasisData.TIMESTAMP == latest.c.TIMESTAMP))
        else:
            modules = DB.session.query(OasisData).filter(OasisData.NODE_ID == id).order_by(OasisData.TIMESTAMP.desc()).limit(1)

        time_end = dt.datetime.now()
        elapsed_time = time_end - time_start
        logger.debug("[database] call database for module page took %s secs",elapsed_time.total_seconds())
        return modules

@app.route('/')
#@cache.cached()
@login_required
def index():
    update_quarantine_cache()
    latest_beat = DB.session.query(OasisHeartbeat).with_entities(OasisHeartbeat.LAST_UPDATE.label('LATEST_BEAT')).all()
    modules = get_modules_data(None).all()
    weather = dashboard.weather_currently()
    raspberrypi = dashboard.raspberrypi()
    nodes = dashboard.nodes(latest_beat)
    farm = dashboard.farm(modules)
    water_tank = wtm.get_current_solenoid_status()
    logger.debug("[weather] %s", weather)
    logger.debug("[raspberrypi] %s", raspberrypi)
    logger.debug("[nodes] %s", nodes)
    logger.debug("[farm] %s", farm)
    logger.debug("[water_tank] %s", water_tank)

    resp = make_response(render_template('index.html',
                                         weather=weather,
                                         water_tank = water_tank,
                                         farm=farm,
                                         raspberrypi=raspberrypi,
                                         nodes=nodes))
    for key,value in analytics.default_param().items():
        resp.set_cookie(key, str(value))
    return resp

@app.route('/module', methods=['GET'])
#@cache.cached(query_string=True)
@login_required
def module():
    update_quarantine_cache()
    id = None
    if 'id' in request.args:
        #example:  http://localhost:8181/module?id=oasis-39732c
        id = request.args['id']
    resp = make_response(render_template('module.html',modules=get_modules_data(id), single=id))
    for key,value in analytics.default_param().items():
        resp.set_cookie(key, str(value))
    return resp


@app.route('/remove', methods=['POST'])
@login_required
def node_remove():
    id = request.form['NODE_ID']
    logger.debug("[remove] %s", id)
    with app.app_context():
        DB.session.query(OasisData).filter(OasisData.NODE_ID==id).delete()
        DB.session.query(OasisHeartbeat).filter(OasisHeartbeat.NODE_ID==id).delete()
        DB.session.commit()
    return json.dumps({'status':'Success!'})

@app.route('/configuration', methods=['POST'])
@login_required
def node_config():
    id = request.form['id']
    logger.debug("[configuration] getting config for %s", id)

    config = None
    with app.app_context():
        latest_db_config = DB.session.query(OasisData).filter(OasisData.NODE_ID==id).order_by(OasisData.TIMESTAMP.desc()).first()
        config = latest_db_config.config()
        oasis_heartbeat = DB.session.query(OasisHeartbeat).filter(OasisHeartbeat.NODE_ID==id).first()
        config["QUARANTINE"] = oasis_heartbeat.quarantine()
        if "LIGHT" in latest_db_config.data():
            config["LIGHT"] = latest_db_config.data()['LIGHT']
        else:
            config["LIGHT"] = -1
    if config is None:
        logger.info("[configuration] no configuration was found in database. Getting defaults")
        DEFAULT_CONFIG_FILE = os.path.join(COMMON_DIR, 'config/oasis.json')
        with open(DEFAULT_CONFIG_FILE, "r") as default_config:
            config = json.load(default_config)
    return json.dumps(config)

@app.route('/training', methods=['POST'])
@login_required
def training():
    message = request.get_json()
    analytics.feedback_online_process(message)
    mqtt.publish("/oasis-inbound", analytics.generate_moisture_req_msg(message))
    return json.dumps({'status':'Success!'})

@app.route('/reset-training', methods=['POST'])
@login_required
def reset_training():
    message = request.get_json()
    analytics.reset_online_process(message)
    return json.dumps({'status':'Success!'})

@app.route('/updatecfg', methods=['POST'])
@login_required
def updatecfg():
    message = json.dumps(request.get_json())
    logger.debug("[updatecfg] %s", message)
    mqtt.publish("/oasis-inbound", message)
    return json.dumps({'status':'Success!'})

@app.route('/reset', methods=['POST'])
@login_required
def reset():
    message = json.dumps(request.get_json())
    logger.debug("[reset] %s", message)
    mqtt.publish("/oasis-inbound", message)
    return json.dumps({'status':'Success!'})


@app.route('/status', methods=['POST'])
@login_required
def refresh():
    message = json.dumps(request.get_json())
    logger.debug("[status] %s", message)
    mqtt.publish("/oasis-inbound", message)
    return json.dumps({'status':'Success!'})

@app.route('/command', methods=['POST'])
#@login_required
def command():
    message = json.dumps(request.get_json())
    logger.debug("[command] %s", message)
    mqtt.publish("/oasis-inbound", message)
    return json.dumps({'status':'Success!'})

@app.route('/command-alexa', methods=['POST'])
@check_if_gui_is_enable
def command_alexa():
    message = request.get_json()
    logger.debug("[command-alexa] %s", message)
    mqtt.publish("/oasis-inbound", message)
    return json.dumps({'status':'Success!'})

@app.route('/firmware', methods=['POST'])
@login_required
def firmware_action():
    message = request.get_json()
    node_id = message["NODE_ID"]
    action = message['ACTION']
    if action ==  "backup":
        logger.info("[firmware-action] BACKUP %s", message)
        message = { "NODE_ID": node_id,
                    "MESSAGE_ID": "backup",
                    "STATUS": ["NODE"]
                   }
        mqtt.publish("/oasis-inbound", json.dumps(message))
        return json.dumps({'status':'success', 'message': 'backup request for '+node_id})

    elif action ==  "upgrade":
        logger.info("[firmware-upgrade] message=%s", message)
        ESP_ADDR = "ESP_ADDR="+message["NODE_IP"]
        ota_output = subprocess.Popen(["make","-f", ESPMAKE_PARAM, "ota",ESP_ADDR],
                                            cwd=NODE_HOME,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE)
        result = str(ota_output.communicate()[0])
        if "failed" in result:
                #/home/msaito/github/makeEspArduino/makeEspArduino.mk:306: recipe for target 'ota' failed
                return json.dumps({'status':'error','message': 'upgrade firmware for '+node_id})
        return json.dumps({'status':'success', 'message': 'upgrade firmware for '+node_id})

    elif action ==  "restore":
        config = OasisData.query.filter(OasisData.NODE_ID==node_id, OasisData.DATA['MESSAGE_ID']=='backup').order_by(OasisData.TIMESTAMP.desc()).first()
        message = { "NODE_ID": node_id,
                    "MESSAGE_ID": "restore",
                    "CONFIG": config.DATA['DATA']['NODE']
                   }
        logger.info("[firmware-restore] TIMESTAMP=%s, CONFIG=%s",config.TIMESTAMP, message)
        mqtt.publish("/oasis-inbound", json.dumps(message))
        return json.dumps({'status':'success', 'message': 'restore request for '+node_id})
    return json.dumps({'status':'error'}), 403;

@app.route("/firmware", methods=['GET'])
@cache.cached()
@login_required
def firmware():
    with app.app_context():
        time_start = dt.datetime.now()
        latest = DB.session.query(OasisData.NODE_ID,
            func.max(OasisData.TIMESTAMP).label('TIMESTAMP')).group_by(OasisData.NODE_ID).subquery('t2')
        modules = DB.session.query(OasisData).join(
            latest, and_(OasisData.NODE_ID == latest.c.NODE_ID,OasisData.TIMESTAMP == latest.c.TIMESTAMP))
        time_end = dt.datetime.now()
        elapsed_time = time_end - time_start
        logger.debug("[database] call database for firmware page took %s secs",elapsed_time.total_seconds())

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


app.register_blueprint(about_system)
app.register_blueprint(management)
app.register_blueprint(monitor)

@app.route('/webhook', methods=['POST'])
def webhook():
    message = request.get_json()

    if message is not None:
        logger.info("[webhook] message:%s",message)
        committer = message["pusher"]["name"]
        commit_message = message["head_commit"]["message"]

        logger.info("[webhook] commit:%s author:%s",commit_message, committer)
        if cfg["MODE"]["AUTO_UPDATE_SERVER"] == True and message["ref"] == cfg["GIT_BRANCH"]:
            logger.info("[webhook] applying update")
            update_server_software()
        else:
            logger.warn("[webhook] auto updates not applied")

        return json.dumps({'status':'request!'})

    return json.dumps({'status':'request was ignored!'})

#curl -i -H "Content-Type: application/json" -X POST -d '{"DIRECTION":"IN", "ACTION":false}' http://localhost:8181/water-tank
@app.route('/water-tank', methods=['POST'])
def water_tank():
    message = request.get_json()
    direction = message["DIRECTION"] # IN or OUT
    action = message['ACTION'] # true or false
    if wtm is None:
        logger.info("[water-tank] Ignoring manually %s command to %s", action, direction)
    else:
        logger.info("[water-tank] %s will be %s", direction, action)
        if direction == "OUT":
            wtm.changeStateWaterTankOut(action)
        else:
            wtm.changeStateWaterTankIn(action)

    return json.dumps({'status':'Success!'})

@app.route('/irrigation')
@login_required
def standard_irrigation():
    #TODO: Thread
    irrigation = Irrigation(logger, cfg, mqtt, socketio, oasis_properties)
    thread = Thread(target=irrigation.run_standard)
    thread.daemon = True
    thread.start()
    return json.dumps({'irrigation':'Started'})

@app.route('/quarantine', methods=['POST'])
@login_required
def quarantine():
    message = request.get_json()
    id = message['NODE_ID']
    change = message['QUARANTINE']

    logger.info("[quarantine] changing %s to %i", id, change)
    with app.app_context():
        DB.session.query(OasisHeartbeat).filter(OasisHeartbeat.NODE_ID==id).update({'QUARANTINE': change})
        DB.session.commit()
    return json.dumps({'status':'Success!'})
###############################################################################
################################# PROCESSORS ##################################
###############################################################################

@app.context_processor
def utility_processor():
    def format_last_update(value):
        return time.strftime("%d/%m/%Y %H:%M:%S", time.localtime(int(value)))
    def status_btn_css(argument):
        switcher = {
            0: "btn-primary",
            1: "btn-danger"
        }
        return switcher.get(argument, "btn-primary disabled")
    def status_btn(argument):
        result =""
        if argument == "DISABLED":
            result = "disabled"
        return result
    def status_node(node_id, last_update, sensor_collect_data_period, water):
        last_update = int(last_update)
        sensor_collect_data_period = 3 * int(sensor_collect_data_period)/1000
        now = int(time.time())
        next_data_is_expected = last_update + sensor_collect_data_period

        if next_data_is_expected >= now: # NEXT is future
            if water:
                return "good irrigation"
            else:
                return "good"
        elif QUARANTINE_CACHE[node_id]:
            return "quarantine"
        else:
            return "danger"
    def status_moisture(node_id, port, level):
        return analytics.status(node_id, port, level)
    def value_moisture_mask(node_id, port, level):
        return analytics.mask(node_id, port, level)
    def weather_icon(argument):
        switcher = {
            "none": "wi wi-na",
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
    def translate_name(node_id):
         if node_id in oasis_properties:
             return oasis_properties[node_id]["name"]
         else:
             return oasis_properties["oasis-undefined"]["name"]
    def description(node_id):
         if node_id in oasis_properties:
             return oasis_properties[node_id]["desc"]
         else:
             return oasis_properties["oasis-undefined"]["desc"]
    def mux_code(node_id, mux):
         if node_id in oasis_properties:
             return oasis_properties[node_id][mux]['cod']
         else:
             return oasis_properties["oasis-undefined"][mux]['cod']
    def quarantine_icon(argument):
        return QUARANTINE_CACHE.get(argument, "")
    return {
            'status_node':status_node,
            'status_moisture':status_moisture,
            'value_moisture_mask':value_moisture_mask,
            'weather_icon': weather_icon,
            'format_last_update':format_last_update,
            'status_btn_css':status_btn_css,
            'status_btn':status_btn,
            'translate_name':translate_name,
            'description':description,
            'mux_code':mux_code,
            'quarantine_icon':quarantine_icon
            }
###############################################################################
############################## HANDLE MQTT ####################################
###############################################################################

# The callback for when the client receives a CONNACK response from the server.
@mqtt.on_connect()
def handle_mqtt_connect(client, userdata, flags, rc):
    logger.info("[MQTT] Connected with result code %s",str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    mqtt.subscribe(cfg["MQTT"]["MQTT_OASIS_TOPIC_HEARTBEAT"])
    mqtt.subscribe(cfg["MQTT"]["MQTT_OASIS_TOPIC_OUTBOUND"])

@mqtt.on_unsubscribe()
def handle_unsubscribe(client, userdata, mid):
    logger.info("[MQTT] Unsubscribed from topic %s !!!", str(mid))

@mqtt.on_disconnect()
def handle_disconnect():
    logger.info("[MQTT] Disconnected!!!")

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
        if isMqttEnabled:
            with app.app_context():
                merged = DB.session.merge(heartbeat)
                QUARANTINE_CACHE[merged.NODE_ID] = merged.QUARANTINE
    if topic == cfg["MQTT"]["MQTT_OASIS_TOPIC_OUTBOUND"]:
        data = OasisData(TIMESTAMP=timestamp,NODE_ID=node_id,DATA=jmsg)
        if "DATA" in jmsg:
            if isMqttEnabled and not QUARANTINE_CACHE[node_id]:
                with app.app_context():
                    #TODO: fixme: somehow this line of code make more stable saving trainning data
                    dbdata = OasisData(TIMESTAMP=timestamp,NODE_ID=node_id,DATA=jmsg)
                    DB.session.merge(dbdata) #avoid data colision due manual status request
            json_data = jmsg["DATA"]
            if "CAPACITIVEMOISTURE" in json_data:
                moisture = json_data["CAPACITIVEMOISTURE"]
                filtered = analytics.gui_noise_filter(node_id, timestamp, moisture)
                data.capacitive_moisture(filtered)
                logger.debug("[data-filtered] %s", filtered)

        json_data = data.toJson()
        socketio.emit('ws-oasis-data', data=json_data)
        logger.debug("[data] %s", json_data)

@mqtt.on_log()
def handle_logging(client, userdata, level, buf):
    logger.debug("[MQTT] %i, %s", level, buf)



###############################################################################
###############################  SCHEDULE #####################################
###############################################################################
#https://medium.com/better-programming/introduction-to-apscheduler-86337f3bb4a6
sched = BackgroundScheduler(daemon=True)

if cfg["SCHEDULE"]["MOISTURE_MONITOR"] != "never":
    def moisture_monitor():
        global mqtt
        global analytics
        global socketio

        #sched.print_jobs()
        advice = analytics.irrigation_advice()
        socketio.emit('ws-server-monitor', data=advice)
        logger.info("[moisture_monitor] %s", advice)
        #mqtt.publish("/schedule-test", "hellllooo")
    moisture_monitor_trigger = CronTrigger.from_crontab(cfg["SCHEDULE"]["MOISTURE_MONITOR"])
    sched.add_job(moisture_monitor, moisture_monitor_trigger)

if cfg["SCHEDULE"]["IRRIGATION_BOT"] != "never":
    irrigation = Irrigation(logger, cfg, mqtt, socketio, oasis_properties)
    irrigation_trigger = CronTrigger.from_crontab(cfg["SCHEDULE"]["IRRIGATION_BOT"])
    logger.info("[irrigation] type: %s", cfg["IRRIGATION"]["TYPE"])
    if cfg["IRRIGATION"]["TYPE"] == "smart":
        sched.add_job(irrigation.run_smart, irrigation_trigger)
    elif cfg["IRRIGATION"]["TYPE"] == "dummy":
        sched.add_job(irrigation.run_dummy, irrigation_trigger)
    else:
        sched.add_job(irrigation.run_standard, irrigation_trigger)

sched.start()

###############################################################################
##################################  START #####################################
###############################################################################
update_quarantine_cache()
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
    #from werkzeug.middleware.profiler import ProfilerMiddleware
    #app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[5], profile_dir='./profile')
    user_reload = False # Avoid Bug: TWICE mqtt instances
    socketio.run(app, host='0.0.0.0', port=8181, debug=cfg["MODE"]["DEBUG"], use_reloader=user_reload)
