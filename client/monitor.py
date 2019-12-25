#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
More complex demonstration of what's possible with the progress bar.
"""
import threading
import time

from prompt_toolkit import HTML
from prompt_toolkit.shortcuts import ProgressBar
from prompt_toolkit.shortcuts.progress_bar import formatters
import simplejson as json

from prompt_toolkit.key_binding import KeyBindings
import paho.mqtt.client as mqtt

from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.widgets import Box, Frame, TextArea

# Layout for displaying hello world.
# (The frame creates the border, the box takes care of the margin/padding.)
root_container = Box(
    Frame(
        TextArea(text="Hello world!\nPress control-c to quit.", width=40, height=10,)
    ),
)
layout = Layout(container=root_container)

# Create custom key bindings first.
kb = KeyBindings()
cancel = [False]

@kb.add('x')
def _(event):
    " Send Abort (control-c) signal. "
    cancel[0] = True

title=HTML("<b>Example of many parallel tasks.</b>")
bottom_toolbar=HTML("<b>[x]</b> Abort.")
custom_formatters = [
    formatters.Label(),
    formatters.Text(" "),
    formatters.SpinningWheel(),
    formatters.Text(" "),
    formatters.Bar(sym_a="|", sym_b="|"),
    formatters.Text(" Value: "),
    formatters.TimeLeft(),
]
#MUX0 = ProgressBar(title=title, bottom_toolbar=bottom_toolbar,formatters=custom_formatters )
MUX0 = ProgressBar()

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    # O subscribe fica no on_connect pois, caso perca a conexão ele a renova
    # Lembrando que quando usado o #, você está falando que tudo que chegar após a barra do topico, será recebido
    client.subscribe("/oasis-outbound")
# Callback responável por receber uma mensagem publicada no tópico acima
def on_message(client, userdata, msg):
    message = json.loads(msg.payload)
    if message["NODE_ID"] == "oasis-39732c":
        #MUX0.set_percentage(int(message["DATA"]["CAPACITIVEMOISTURE"]["MUX0"]))
        print(int(message["DATA"]["CAPACITIVEMOISTURE"]["MUX0"])/100)
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
# Conecta no MQTT Broker, no meu caso, o Mosquitto
client.connect("192.168.1.70", 1883, 60)

def main():
    app = Application(full_screen=False)
    app.run()
    client.loop_forever()




if __name__ == "__main__":
    main()
