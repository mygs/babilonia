#!/usr/bin/python3
import paho.mqtt.client as mqtt
import database
import time
import os
import json
import logging
import logging.config

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    logger.info("Connected with result code %s",str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("/online")
    client.subscribe("/data")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    topic = msg.topic
    data = str(msg.payload, 'utf-8')
    values = dict(item.split(":") for item in data.split(";"))
    logger.info("Receive message from NODE %s on topic %s",values['id'], topic)

    if topic == "/data":
        database.insert_data(values)
    if topic == "/online":
        if values['rb'] == "0" : # not remote requested boot
            conf = ""
            conf = database.retrieve_cfg(values)
            client.publish("/cfg", conf)



#################################
###########    MAIN   ###########
#################################
print("*** STARTING NABUCODONOSOR SYSTEM ***")
# create console handler and set level to debug
project_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(project_dir, 'logging.json'), "r") as fd:
    logging.config.dictConfig(json.load(fd))
logger = logging.getLogger()

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("192.168.1.60", 1883, 60) #nabucodonosor

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
