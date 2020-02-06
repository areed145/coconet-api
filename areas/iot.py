import os
import numpy as np
import pandas as pd
from pymongo import MongoClient
import plotly
import plotly.graph_objs as go
import json
from datetime import datetime, timedelta
from utils import config, helpers
from scipy import signal


def create_graph_iot(sensor, time):
    client = MongoClient(os.environ['MONGODB_CLIENT'])
    start, now = helpers.get_time_range(time)
    db = client.iot
    df = pd.DataFrame(
        list(db.raw.find({'entity_id': {'$in': sensor}, 'timestamp_': {'$gt': start, '$lte': now}}).sort([('timestamp_', -1)])))
    if len(df) == 0:
        df = pd.DataFrame(list(db.raw.find(
            {'entity_id': {'$in': sensor}}).limit(2).sort([('timestamp_', -1)])))

    data = []
    for s in sensor:
        try:
            df_s = df[df['entity_id'] == s]
            data.append(
                go.Scatter(
                    x=df_s['timestamp_'],
                    y=df_s['state'],
                    name=df_s['entity_id'].values[0],
                    line=dict(
                        shape='spline',
                        smoothing=0.7,
                        width=3
                    ),
                    mode='lines'
                )
            )
        except:
            pass

    layout = go.Layout(
        autosize=True,
        colorway=config.colorway,
        font=dict(family='Ubuntu'),
        showlegend=True,
        legend=dict(orientation='h'),
        xaxis=dict(range=[start, now]),
        hovermode='closest',
        hoverlabel=dict(font=dict(family='Ubuntu')),
        uirevision=True,
        margin=dict(r=50, t=30, b=30, l=60, pad=0),
    )
    try:
        graphJSON = json.dumps(dict(data=data, layout=layout),
                               cls=plotly.utils.PlotlyJSONEncoder)
    except:
        graphJSON = None
    client.close()
    return graphJSON


def create_spectrogram_iot(sensor, time):
    client = MongoClient(os.environ['MONGODB_CLIENT'])
    start, now = helpers.get_time_range(time)
    db = client.iot
    df = pd.DataFrame(
        list(db.raw.find({'entity_id': {'$in': sensor}, 'timestamp_': {'$gt': start, '$lte': now}}).sort([('timestamp_', -1)])))
    if len(df) == 0:
        df = pd.DataFrame(list(db.raw.find(
            {'entity_id': {'$in': sensor}}).limit(2).sort([('timestamp_', -1)])))

    data = []
    data_spectro = []
    for s in sensor:
        try:
            df_s = df[df['entity_id'] == s]
            df_s.index = df_s['timestamp_']
            df_s = df_s.resample('1S').mean()
            data.append(
                go.Scatter(
                    x=df_s['timestamp_'],
                    y=df_s['state'],
                    name=df_s['entity_id'].values[0],
                    line=dict(
                        shape='spline',
                        smoothing=0.7,
                        width=3
                    ),
                    mode='lines'
                )
            )
            f, t, Sxx = signal.spectrogram(df_s['state'], fs=1.0)
            data_spectro.extend(
                [
                    go.Heatmap(
                        x=t,
                        y=f,
                        z=Sxx,
                        name=df_s['entity_id'].values[0],
                        line=dict(
                            shape='spline',
                            smoothing=0.7,
                            width=3
                        ),
                        mode='lines'
                    )
                ]
            )
        except:
            pass

    layout = go.Layout(
        autosize=True,
        colorway=config.colorway,
        font=dict(family='Ubuntu'),
        showlegend=True,
        legend=dict(orientation='h'),
        xaxis=dict(range=[start, now]),
        hovermode='closest',
        hoverlabel=dict(font=dict(family='Ubuntu')),
        uirevision=True,
        margin=dict(r=50, t=30, b=30, l=60, pad=0),
    )
    try:
        graphJSON = json.dumps(dict(data=data, layout=layout),
                               cls=plotly.utils.PlotlyJSONEncoder)
    except:
        graphJSON = None
    client.close()
    return graphJSON


def create_anomaly_iot(sensor, time):
    client = MongoClient(os.environ['MONGODB_CLIENT'])
    start, now = helpers.get_time_range(time)
    db = client.iot
    df = pd.DataFrame(
        list(db.raw.find({'entity_id': {'$in': sensor}, 'timestamp_': {'$gt': start, '$lte': now}}).sort([('timestamp_', -1)])))
    if len(df) == 0:
        df = pd.DataFrame(list(db.raw.find(
            {'entity_id': {'$in': sensor}}).limit(2).sort([('timestamp_', -1)])))

    data = []
    for s in sensor:
        try:
            df_s = df[df['entity_id'] == s]
            data.append(
                go.Scatter(
                    x=df_s['timestamp_'],
                    y=df_s['state'],
                    name=df_s['entity_id'].values[0],
                    line=dict(
                        shape='spline',
                        smoothing=0.7,
                        width=3
                    ),
                    mode='lines'
                )
            )
        except:
            pass

    layout = go.Layout(
        autosize=True,
        colorway=config.colorway,
        font=dict(family='Ubuntu'),
        showlegend=True,
        legend=dict(orientation='h'),
        xaxis=dict(range=[start, now]),
        hovermode='closest',
        hoverlabel=dict(font=dict(family='Ubuntu')),
        uirevision=True,
        margin=dict(r=50, t=30, b=30, l=60, pad=0),
    )
    try:
        graphJSON = json.dumps(dict(data=data, layout=layout),
                               cls=plotly.utils.PlotlyJSONEncoder)
    except:
        graphJSON = None
    client.close()
    return graphJSON
