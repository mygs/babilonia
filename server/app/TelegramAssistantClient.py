#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os, json, requests
from TelegramAssistantServer import *

SERVER_HOME = os.path.dirname(os.path.abspath(__file__))
COMMON_DIR=os.path.join(SERVER_HOME, '../../common')
os.chdir(SERVER_HOME) #change directory because of log files
with open(os.path.join(SERVER_HOME, 'config.json'), "r") as config_json_file:
    cfg = json.load(config_json_file)

def send_monitor_message(message):
    monitor_url = cfg["TELEGRAM"]["MONITOR_URL"]
    headers = {'Content-type': 'application/json'}
    requests.post(monitor_url,data=json.dumps(message), headers=headers)

if __name__ == '__main__':
    message = {}
    message['SOURCE'] = "TEST_CLIENT"
    message['MESSAGE'] = "MESSAGE CONTENT CAN BE <b>BOLD</b>"
    TelegramAssistantServer.send_monitor_message(message)
    #TelegramAssistantServer.send_monitor_message({'SOURCE': 'TEST_CLIENT','MESSAGE': 'Starting system at '+os.uname()[1]})
