#!/usr/bin/python3
# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
"""
import random

from pygments.lexers.html import HtmlLexer

from prompt_toolkit.application import Application
from prompt_toolkit.application.current import get_app
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.layout.containers import Float, HSplit, VSplit
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.menus import CompletionsMenu
from prompt_toolkit.styles import Style
from prompt_toolkit.shortcuts.progress_bar import formatters
import simplejson as json
import paho.mqtt.client as mqtt
from prompt_toolkit.widgets import (
    Box,
    Frame,
    Label,
    MenuContainer,
    MenuItem,
    ProgressBar
)

MUX0 = ProgressBar()
MUX1 = ProgressBar()
MUX2 = ProgressBar()
MUX3 = ProgressBar()
MUX4 = ProgressBar()
MUX5 = ProgressBar()
MUX6 = ProgressBar()
MUX7 = ProgressBar()

def on_connect(client, userdata, flags, rc):
    client.subscribe("/oasis-outbound")
def on_message(client, userdata, msg):
    message = json.loads(msg.payload)
    if message["NODE_ID"] == "oasis-39732c":
        #MUX0.percentage = int(message["DATA"]["CAPACITIVEMOISTURE"]["MUX0"])/100
        MUX0.percentage = int(random.uniform(0, 100))
        MUX1.percentage = int(random.uniform(0, 100))
        MUX2.percentage = int(random.uniform(0, 100))
        MUX3.percentage = int(random.uniform(0, 100))
        MUX4.percentage = int(random.uniform(0, 100))
        MUX5.percentage = int(random.uniform(0, 100))
        MUX6.percentage = int(random.uniform(0, 100))
        MUX7.percentage = int(random.uniform(0, 100))
        get_app().invalidate()

def exitX(event):
    get_app().exit(result=True)

def accept_yes():
    get_app().exit(result=True)

def accept_no():
    get_app().exit(result=False)

def do_exit():
    get_app().exit(result=False)


root_container = HSplit(
    [
        Frame(body=MUX0, title="MUX0"),
        Frame(body=MUX1, title="MUX1"),
        Frame(body=MUX2, title="MUX2"),
        Frame(body=MUX3, title="MUX3"),
        Frame(body=MUX4, title="MUX4"),
        Frame(body=MUX5, title="MUX5"),
        Frame(body=MUX6, title="MUX6"),
        Frame(body=MUX7, title="MUX7"),
    ]
)

root_container = MenuContainer(
    body=root_container,
    menu_items=[
        MenuItem(
            "File",
            children=[
                MenuItem("New"),
                MenuItem(
                    "Open",
                    children=[
                        MenuItem("From file..."),
                        MenuItem("From URL...")
                    ],
                ),
                MenuItem("-", disabled=True),
                MenuItem("Exit", handler=do_exit),
            ],
        ),
        MenuItem("View", children=[MenuItem("Status Bar"),]),
        MenuItem("Info", children=[MenuItem("About"),]),
    ],
    floats=[
        Float(
            xcursor=True,
            ycursor=True,
            content=CompletionsMenu(max_height=16, scroll_offset=1),
        ),
    ],
)

# Global key bindings.
bindings = KeyBindings()
bindings.add("tab")(focus_next)
bindings.add("s-tab")(focus_previous)
bindings.add("x")(exitX)


style = Style.from_dict(
    {
        "window.border": "#888888",
        "shadow": "bg:#222222",
        "menu-bar": "bg:#aaaaaa #888888",
        "menu-bar.selected-item": "bg:#ffffff #000000",
        "menu": "bg:#888888 #ffffff",
        "menu.border": "#aaaaaa",
        "window.border shadow": "#444444",
        "focused  button": "bg:#880000 #ffffff noinherit",
        # Styling for Dialog widgets.
        "radiolist focused": "noreverse",
        "radiolist focused radio.selected": "reverse",
        "button-bar": "bg:#aaaaff",
    }
)


application = Application(
    layout=Layout(root_container,focused_element=None),
    key_bindings=bindings,
    style=style,
    mouse_support=False,
    full_screen=True,
)
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
# Conecta no MQTT Broker, no meu caso, o Mosquitto
client.connect("192.168.1.70", 1883, 60)
client.loop_start()

def run():
    result = application.run()
    print("You said: %r" % result)

if __name__ == "__main__":
    run()
