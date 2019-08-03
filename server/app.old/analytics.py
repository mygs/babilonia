#!/usr/bin/python3
import simplejson as json
import database as db
import pandas as pd
import pytz
from pandas.core.frame import DataFrame

def get_timeseries(id):

    data = db.retrieve_data(id);
    df = DataFrame(list(data))
    df.columns = ['timestamp', 'temperature', 'humidity']
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    df['temperature'] = pd.to_numeric(df['temperature'])
    df['humidity'] = pd.to_numeric(df['humidity'])

    df.index = df['timestamp']
    df.index = df.index.tz_localize(pytz.utc).tz_convert(pytz.timezone('America/Sao_Paulo'))


    df = df.resample('30Min').mean()
    df = df.ix[-48:] # "1 day afterwards"
    df = df[pd.notnull(df['temperature'])] # remove null data points

    df.index = df.index.strftime('%H:%M')
    label = df.index.format()
    temperature = [{"label":label,"data":df.temperature.tolist()}]
    humidity = [{"label":label,"data":df.humidity.tolist()}]
    timeseries = [{"temperature":temperature,
                   "humidity":humidity}]
    return json.dumps(timeseries)
