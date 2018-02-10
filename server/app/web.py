#!/usr/bin/python3
from flask import Flask, render_template, request
from flaskext.mysql import MySQL
import os
import json
import database
import time

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
