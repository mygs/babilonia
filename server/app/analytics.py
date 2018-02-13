#!/usr/bin/python3
import simplejson as json
import database as db
import pandas as pd
import pytz
from pandas.core.frame import DataFrame

def get_timeseries(id):

    data = db.retrieve_data(id);
    df = DataFrame(list(data))
    df.columns = ['timestamp', 'temperature', 'humidity', 'moisture']
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s', utc=True)
    df['temperature'] = pd.to_numeric(df['temperature'])
    df['humidity'] = pd.to_numeric(df['humidity'])
    df['moisture'] = pd.to_numeric(df['moisture'])

    df.index = df['timestamp']
    df.index = df.index.tz_localize(pytz.utc).tz_convert(pytz.timezone('America/Sao_Paulo'))


    df = df.resample('30Min').mean()
    df = df.ix[-48:] # "1 day afterwards"
    df = df[pd.notnull(df['temperature'])] # remove null data points

    df.index = df.index.strftime('%H:%M')
    label = df.index.format()
    data = df.temperature.tolist()
    temperature = [{"label":label,"data":data}]
    timeseries = [{"temperature":temperature}]
    return json.dumps(timeseries)
