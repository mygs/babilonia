#!/usr/bin/python3
from flask import Flask, render_template, request
from flaskext.mysql import MySQL
import os
import simplejson as json
import database
import time
import paho.mqtt.client as mqtt


project_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(project_dir, 'config.json'), "r") as json_data_file:
    cfg = json.load(json_data_file)

mysql = MySQL()
app = Flask(__name__)

app.config['MYSQL_DATABASE_USER'] =  cfg["db"]["user"]
app.config['MYSQL_DATABASE_PASSWORD'] =  cfg["db"]["password"]
app.config['MYSQL_DATABASE_DB'] = cfg["db"]["schema"]
app.config['MYSQL_DATABASE_HOST'] = cfg["db"]["host"]
mysql.init_app(app)



@app.route('/')
def index():
    modules = database.retrieve_last_telemetry_info();
    return render_template('index.html', modules=modules)

@app.route('/configuration', methods=['POST'])
def node():
    id = request.form['id'];
    node = database.get_node_cfg(id);
    return json.dumps({ 'NAME':node[0],
                        'TEMPERATURE_THRESHOLD':node[1],
                        'MOISTURE_THRESHOLD':node[2],
                        'MASK_CRON_LIGHT_ON':node[3],
                        'MASK_CRON_LIGHT_OFF':node[4],
                        'MASK_CRON_CTRL':node[5]});

@app.route('/updatecfg', methods=['POST'])
def updatecfg():

    status = database.save_cfg(request);
    return json.dumps({ 'status':status});


@app.route('/light', methods=['POST'])
def light():
    client = mqtt.Client()
    client.connect(cfg["mqtt"]["broker"], cfg["mqtt"]["port"], cfg["mqtt"]["keepalive"]) #nabucodonosor
    id = request.form['id'];
    command = request.form['command'];
    client.publish("/cfg", "id:{};light:{}".format(id, command))
    return json.dumps({'status':'OK','id':id,'command':command});


@app.route('/command', methods=['POST'])
def command():
    client = mqtt.Client()
    client.connect(cfg["mqtt"]["broker"], cfg["mqtt"]["port"], cfg["mqtt"]["keepalive"]) #nabucodonosor
    id = request.form['id'];
    code = request.form['code'];
    client.publish("/cfg", "id:{};cmd:{}".format(id, code))
    return json.dumps({'status':'OK','id':id,'code':code});

@app.context_processor
def utility_processor():
    def format_timestamp(value):
        return time.strftime("%d-%m-%y %H:%M", time.localtime(int(value)))
    def format_temperature(value):
        return u'{0:.2f} C'.format(value)
    def format_humidity(value):
        return u'{0:.2f} %'.format(value)
    def format_moisture(value):
        return u'{0:.2f} %'.format(value)
    def status(value):
        if int(value) == 1:
            return "ON"
        else:
            return "OFF"
    return {'format_timestamp':format_timestamp,
            'format_temperature':format_temperature,
            'format_humidity':format_humidity,
            'format_moisture':format_moisture,
            'status':status,
            }


@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)
