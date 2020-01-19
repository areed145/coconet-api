import os
import numpy as np
import pandas as pd
from pymongo import MongoClient
import gridfs
import plotly
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import json
from datetime import datetime, timedelta
import base64
import re
# import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap, rgb2hex, to_rgba

mapbox_access_token = os.environ['MAPBOX_TOKEN']

colorway = [
    '#b8fb3c',
    '#5ce5d5',
    '#fe53bb',
    '#7898fb',
    # '#001437',
    '#09fbd3',
    '#f5d300',
    '#3cb9fc',
    '#b537f2',
    '#8a2be2',
    # '#120052',
    '#08f7fe',
    '#09fbd3',
    '#fe53bb',
]

cs_normal = [
    [0.0, '#424ded'],
    [0.1, '#4283ed'],
    [0.2, '#42d0ed'],
    [0.3, '#42edae'],
    [0.4, '#78ed42'],
    [0.5, '#d6ed42'],
    [0.6, '#edde42'],
    [0.7, '#f4af41'],
    [0.8, '#f48541'],
    [0.9, '#f44741'],
    [1.0, '#f44298']
]

cs_rdgn = [
    [0.0, '#f44741'],
    [0.2, '#f48541'],
    [0.4, '#f4af41'],
    [0.6, '#edde42'],
    [0.8, '#d6ed42'],
    [1.0, '#78ed42']
]

cs_gnrd = [
    [0.0, '#78ed42'],
    [0.2, '#d6ed42'],
    [0.4, '#edde42'],
    [0.6, '#f4af41'],
    [0.8, '#f48541'],
    [1.0, '#f44741'],
]

cs_gnylrd = [
    [0.0, '#21d411'],
    [0.4, '#21d411'],
    [0.45, '#f7e926'],
    [0.475, '#f67513'],
    [0.525, '#ed0c0c'],
    [0.55, '#f613e7'],
    [1.0, '#f613e7']
]

cs_circle = [
    [0.000, '#f45f42'],
    [0.067, '#f7856f'],
    [0.133, '#e2aba1'],
    [0.200, '#d8bdb8'],
    [0.267, '#BCBCBC'],
    [0.333, '#bac8e0'],
    [0.400, '#aeccfc'],
    [0.467, '#77aaf9'],
    [0.533, '#4186f4'],
    [0.600, '#77aaf9'],
    [0.667, '#aeccfc'],
    [0.733, '#bac8e0'],
    [0.800, '#BCBCBC'],
    [0.867, '#d8bdb8'],
    [0.933, '#e2aba1'],
    [1.000, '#f7856f'],
]

cs_updown = [
    [0.000, '#4186f4'],
    [0.125, '#77aaf9'],
    [0.250, '#aeccfc'],
    [0.375, '#bac8e0'],
    [0.500, '#BCBCBC'],
    [0.625, '#d8bdb8'],
    [0.750, '#e2aba1'],
    [0.875, '#f7856f'],
    [1.000, '#f45f42'],
]

cs_circle = [
    [0.000, '#ff4336'],
    [0.067, '#ff7936'],
    [0.133, '#ffaf36'],
    [0.200, '#ffc636'],
    [0.267, '#ffee36'],
    [0.333, '#d0ff36'],
    [0.400, '#a5ff36'],
    [0.467, '#72ff36'],
    [0.533, '#36ff43'],
    [0.600, '#36ffa5'],
    [0.667, '#36ffff'],
    [0.733, '#36d0ff'],
    [0.800, '#368aff'],
    [0.867, '#bf36ff'],
    [0.933, '#ff36c6'],
    [1.000, '#ff3665'],
]

scl_oil = [
    [0.00, '#d6ed42'],
    [0.10, '#78ed42'],
    [0.50, '#50bf37'],
    [1.00, '#06721e']
]

scl_oil_log = [
    [0, '#dbdbdb'],  # 0
    [1./1000, '#d6ed42'],  # 10
    [1./100, '#78ed42'],  # 100
    [1./10, '#50bf37'],  # 1000
    [1., '#06721e']  # 10000
]

scl_wtr = [
    [0.00, '#caf0f7'],
    [0.33, '#64d6ea'],
    [0.66, '#4286f4'],
    [1.00, '#0255db']
]

scl_wtr_log = [
    [0, '#dbdbdb'],  # 0
    [1./1000, '#caf0f7'],  # 10
    [1./100, '#64d6ea'],  # 100
    [1./10, '#4286f4'],  # 1000
    [1., '#0255db']  # 10000
]

scl_gas = [
    [0.00, '#fcbfbf'],
    [0.33, '#f28282'],
    [0.66, '#ef2626'],
    [1.00, '#7a0707']
]

scl_stm = [
    [0.00, '#edb6d7'],
    [0.33, '#ed87c4'],
    [0.66, '#e22f9b'],
    [1.00, '#930b5d']
]

scl_stm_log = [
    [0, '#dbdbdb'],  # 0
    [1./1000, '#edb6d7'],  # 10
    [1./100, '#ed87c4'],  # 100
    [1./10, '#e22f9b'],  # 1000
    [1., '#930b5d']  # 10000
]

scl_cyc = [
    [0.00, '#fff1c6'],
    [0.33, '#f7dd8a'],
    [0.66, '#fcd555'],
    [1.00, '#ffc300']
]


def get_time_range(time):
    unit = time[0]
    val = int(time[2:])
    now = datetime.utcnow()
    if unit == 'm':
        start = now - timedelta(minutes=val)
    if unit == 'h':
        start = now - timedelta(hours=val)
    if unit == 'd':
        start = now - timedelta(days=val)
    if unit == 'o':
        start = now - timedelta(months=val)
    return start, now


def create_3d_plot(df, x, y, z, cs, x_name, y_name, z_name, x_color, y_color, z_color):
    df = df[(df[x] > -9999) & (df[x] < 9999) &
            (df[y] > -9999) & (df[y] < 9999) &
            (df[z] > -9999) & (df[z] < 9999)]

    df[x+'_u'] = np.round(df[x], 1)
    df[y+'_u'] = np.round(df[y], 1)
    df[z+'_u'] = np.round(df[z], 1)

    df = pd.pivot_table(df, values=z+'_u', index=[
        x+'_u'], columns=[y+'_u'], aggfunc=np.mean)

    data = [
        go.Surface(
            x=df.index.values,
            y=df.columns.values,
            z=df.values,
            colorscale=cs,
            connectgaps=True,
        ),
    ]

    layout = go.Layout(
        autosize=True,
        margin=dict(r=10, t=10, b=10, l=10, pad=0),
        hoverlabel=dict(
            font=dict(
                family='Ubuntu'
            )
        ),
        scene={'aspectmode': 'cube',
               'xaxis': {
                   'title': x_name,
                   'tickfont': {'family': 'Ubuntu', 'size': 10},
                   'titlefont': {'family': 'Ubuntu', 'color': x_color},
                   'type': 'linear'
               },
               'yaxis': {
                   'title': y_name,
                   'tickfont': {'family': 'Ubuntu', 'size': 10},
                   'titlefont': {'family': 'Ubuntu', 'color': y_color},
                   'tickangle': 1
               },
               'zaxis': {
                   'title': z_name,
                   'tickfont': {'family': 'Ubuntu', 'size': 10},
                   'titlefont': {'family': 'Ubuntu', 'color': z_color},
               },
               }
    )
    graphJSON = json.dumps(dict(data=data, layout=layout),
                           cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


def create_graph_iot(sensor, time):
    client = MongoClient(os.environ['MONGODB_CLIENT'])
    start, now = get_time_range(time)
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
        colorway=colorway,
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


def get_prodinj(wells):
    client = MongoClient(os.environ['MONGODB_CLIENT'])
    db = client.petroleum
    docs = db.doggr.aggregate(
        [{'$unwind': '$prodinj'}, {'$match': {'api': {'$in': wells}}}, ])
    df = pd.DataFrame()
    for x in docs:
        doc = dict(x)
        df_ = pd.DataFrame(doc['prodinj'])
        df_['api'] = doc['api']
        df = df.append(df_)

    df.sort_values(by=['api', 'date'], inplace=True)
    df.reset_index(drop=True, inplace=True)
    df.fillna(0, inplace=True)

    for col in ['date', 'oil', 'water', 'gas', 'oilgrav', 'pcsg', 'ptbg', 'btu', 'steam', 'water_i', 'cyclic', 'gas_i', 'air', 'pinjsurf']:
        if col not in df:
            df[col] = 0
        if col not in ['date', 'oilgrav', 'pcsg', 'ptbg', 'btu', 'pinjsurf']:
            df[col] = df[col]/30.45
    client.close()
    return df


def get_offsets_oilgas(api, radius, axis):
    client = MongoClient(os.environ['MONGODB_CLIENT'])
    db = client.petroleum
    docs = db.doggr.find(
        {'api': api}, {'api': 1, 'latitude': 1, 'longitude': 1})
    for x in docs:
        header = dict(x)
    try:
        r = radius/100
        lat = header['latitude']
        lon = header['longitude']
        df = pd.DataFrame(list(db.doggr.find({'latitude': {'$gt': lat-r, '$lt': lat+r},
                                              'longitude': {'$gt': lon-r, '$lt': lon+r}})))
        df['dist'] = np.arccos(np.sin(lat*np.pi/180) * np.sin(df['latitude']*np.pi/180) + np.cos(lat*np.pi/180)
                               * np.cos(df['latitude']*np.pi/180) * np.cos((df['longitude']*np.pi/180) - (lon*np.pi/180))) * 6371
        df = df[df['dist'] <= radius]
        df.sort_values(by='dist', inplace=True)
        offsets = df['api'].tolist()
        dists = df['dist'].tolist()

        df_offsets = pd.DataFrame()
        for idx in range(len(df)):
            try:
                df_ = pd.DataFrame(df['prodinj'].iloc[idx])
                df_['api'] = df['api'].iloc[idx]
                df_['date'] = pd.to_datetime(df_['date'])
                df_offsets = df_offsets.append(df_)
            except:
                pass

        df_offsets['distapi'] = df_offsets['api'].apply(
            lambda x: str(np.round(dists[offsets.index(x)], 3))+' mi - '+x)
        df_offsets.sort_values(by='distapi', inplace=True)

        def ci_plot(df_offsets, prop, api, c1, c2, c3):
            df_ci = df_offsets.pivot_table(
                index='date', columns='api', values=prop)
            df_ci = df_ci.replace(0, pd.np.nan)
            df_ci = df_ci / 30.45
            # df_mean = df_ci.mean(axis=1)
            # df_std = df_ci.std(axis=1)
            # ci_lb = df_mean - df_std
            # ci_ub = df_mean + df_std
            count = df_ci.count(axis=1).fillna(0)
            sums = df_ci.sum(axis=1).fillna(0)
            ci_lb = df_ci.quantile(0.25, axis=1).fillna(0)
            ci_ub = df_ci.quantile(0.75, axis=1).fillna(0)
            val = df_ci[api]

            return [
                go.Scatter(
                    x=df_ci.index,
                    y=ci_ub,
                    name='offest_upper_75ci',
                    fill=None,
                    mode='lines',
                    line=dict(
                        color=c1,
                        shape='spline',
                        smoothing=0.3,
                        width=3
                    ),
                ),
                go.Scatter(
                    x=df_ci.index,
                    y=ci_lb,
                    name='offset_lower_75ci',
                    fill='tonexty',
                    mode='lines',
                    line=dict(
                        color=c1,
                        shape='spline',
                        smoothing=0.3,
                        width=3
                    ),
                ),
                go.Scatter(
                    x=df_ci.index,
                    y=count,
                    name='offset_count',
                    mode='lines',
                    line=dict(
                        color='#8c8c8c',
                        shape='spline',
                        smoothing=0.3,
                        width=3
                    ),
                ),
                go.Scatter(
                    x=df_ci.index,
                    y=sums,
                    name='offset_sum',
                    mode='lines',
                    line=dict(
                        color=c2,
                        shape='spline',
                        smoothing=0.3,
                        width=3
                    ),
                ),
                go.Scatter(
                    x=df_ci.index,
                    y=val,
                    name='current_well',
                    mode='lines',
                    line=dict(
                        color=c3,
                        shape='spline',
                        smoothing=0.3,
                        width=3
                    ),
                )
            ]

        data_offset_oil = [
            go.Heatmap(
                z=df_offsets['oil']/30.45,
                x=df_offsets['date'],
                y=df_offsets['distapi'],
                colorscale=scl_oil_log,
            ),
        ]

        data_offset_stm = [
            go.Heatmap(
                z=df_offsets['steam']/30.45,
                x=df_offsets['date'],
                y=df_offsets['distapi'],
                colorscale=scl_stm_log,
            ),
        ]

        data_offset_wtr = [
            go.Heatmap(
                z=df_offsets['water']/30.45,
                x=df_offsets['date'],
                y=df_offsets['distapi'],
                colorscale=scl_wtr_log,
            ),
        ]

        layout = go.Layout(
            autosize=True,
            font=dict(family='Ubuntu'),
            hoverlabel=dict(font=dict(family='Ubuntu')),
            margin=dict(r=10, t=10, b=30, l=150, pad=0),
            yaxis=dict(autorange='reversed'),
            showlegend=False,
        )
        if axis == 'log':
            layout_ = go.Layout(
                autosize=True,
                font=dict(family='Ubuntu'),
                hoverlabel=dict(font=dict(family='Ubuntu')),
                showlegend=True,
                legend=dict(orientation='h'),
                yaxis=dict(type='log'),
                margin=dict(r=50, t=30, b=30, l=60, pad=0),
            )
        else:
            layout_ = go.Layout(
                autosize=True,
                font=dict(family='Ubuntu'),
                hoverlabel=dict(font=dict(family='Ubuntu')),
                showlegend=True,
                legend=dict(orientation='h'),
                margin=dict(r=50, t=30, b=30, l=60, pad=0),
            )

        graphJSON_offset_oil = json.dumps(dict(data=data_offset_oil, layout=layout),
                                          cls=plotly.utils.PlotlyJSONEncoder)
        graphJSON_offset_stm = json.dumps(dict(data=data_offset_stm, layout=layout),
                                          cls=plotly.utils.PlotlyJSONEncoder)
        graphJSON_offset_wtr = json.dumps(dict(data=data_offset_wtr, layout=layout),
                                          cls=plotly.utils.PlotlyJSONEncoder)
        graphJSON_offset_oil_ci = json.dumps(dict(data=ci_plot(df_offsets, 'oil', header['api'], scl_oil[0][1], scl_oil[1][1], scl_oil[2][1]), layout=layout_),
                                             cls=plotly.utils.PlotlyJSONEncoder)
        graphJSON_offset_wtr_ci = json.dumps(dict(data=ci_plot(df_offsets, 'water', header['api'], scl_wtr[0][1], scl_wtr[1][1], scl_wtr[2][1]), layout=layout_),
                                             cls=plotly.utils.PlotlyJSONEncoder)
        graphJSON_offset_stm_ci = json.dumps(dict(data=ci_plot(df_offsets, 'steam', header['api'], scl_stm[0][1], scl_stm[1][1], scl_stm[2][1]), layout=layout_),
                                             cls=plotly.utils.PlotlyJSONEncoder)

    except:
        graphJSON_offset_oil = None
        graphJSON_offset_stm = None
        graphJSON_offset_wtr = None
        graphJSON_offset_oil_ci = None
        graphJSON_offset_stm_ci = None
        graphJSON_offset_wtr_ci = None
        offsets = None

    map_offsets = None
    client.close()
    return graphJSON_offset_oil, graphJSON_offset_stm, graphJSON_offset_wtr, graphJSON_offset_oil_ci, graphJSON_offset_stm_ci, graphJSON_offset_wtr_ci, map_offsets, offsets


def get_crm(api):
    client = MongoClient(os.environ['MONGODB_CLIENT'])
    db = client.petroleum
    docs = db.doggr.find({'api': api}, {'crm': 1})
    for x in docs:
        header = dict(x)
    try:
        df = pd.DataFrame(header['crm']['cons'])
        df['gain'] = df['gain'].apply(lambda x: '%.3f' % x)
        df['gain'] = df['gain'].astype(float)
        df['dist'] = np.arccos(
            np.sin(df['y0']*np.pi/180) *
            np.sin(df['y1']*np.pi/180) +
            np.cos(df['y0']*np.pi/180) *
            np.cos(df['y1']*np.pi/180) *
            np.cos((df['x1']*np.pi/180) - (df['x0']*np.pi/180))) * 6371
        df['distapi'] = df.apply(lambda x: str(
            np.round(x['dist'], 3))+' mi - '+str(x['to']), axis=1)
        df = df.sort_values(by='distapi', ascending=True).reset_index()
        xs = df['gain']
        ys = df['distapi']
        data = [
            go.Bar(
                y=ys,
                x=xs,
                name='crm_gains',
                orientation='h',
                marker=dict(
                    color=xs,
                    colorscale=cs_gnylrd,
                    cmin=0,
                    cmax=1,
                )
            )
        ]
        layout = go.Layout(
            autosize=True,
            font=dict(family='Ubuntu'),
            hoverlabel=dict(font=dict(family='Ubuntu')),
            margin=dict(r=10, t=10, b=30, l=150, pad=0),
            xaxis=dict(
                # range=[0, 1],
                categoryorder='array',
                categoryarray=[x for _, x in sorted(zip(ys, xs))]
            ),
            yaxis=dict(autorange='reversed'),
            showlegend=False,
        )
        graphJSON_crm = json.dumps(
            dict(data=data, layout=layout), cls=plotly.utils.PlotlyJSONEncoder)
    except:
        graphJSON_crm = None
    client.close()
    return graphJSON_crm


def get_cyclic_jobs(api):
    client = MongoClient(os.environ['MONGODB_CLIENT'])
    db = client.petroleum
    docs = db.doggr.find({'api': api}, {'cyclic_jobs': 1})
    for x in docs:
        header = dict(x)
    try:
        df_cyclic = pd.DataFrame(header['cyclic_jobs'])
        fig_cyclic_jobs = make_subplots(rows=2, cols=1)
        total = len(df_cyclic)
        c0 = np.array([245/256, 200/256, 66/256, 1])
        c1 = np.array([245/256, 218/256, 66/256, 1])
        c2 = np.array([188/256, 245/256, 66/256, 1])
        c3 = np.array([108/256, 201/256, 46/256, 1])
        c4 = np.array([82/256, 138/256, 45/256, 1])
        c5 = np.array([24/256, 110/256, 45/256, 1])
        cm = LinearSegmentedColormap.from_list(
            'custom', [c0, c1, c2, c3, c4, c5], N=total)
        df_cyclic.sort_values(by='number', inplace=True)
        for idx in range(len(df_cyclic)):
            try:
                color = rgb2hex(cm(df_cyclic['number'][idx]/total))
                prod = pd.DataFrame(df_cyclic['prod'][idx])
                prod = prod/30.45
                fig_cyclic_jobs.add_trace(
                    go.Scatter(
                        x=prod.index,
                        y=prod['oil']-prod['oil'].loc['0'],
                        name=df_cyclic['start'][idx][:10],
                        mode='lines',
                        line=dict(
                            color=color,
                            shape='spline',
                            smoothing=0.3,
                            width=3
                        ),
                        legendgroup=str(df_cyclic['number'][idx]),
                    ),
                    row=1, col=1,
                )
                fig_cyclic_jobs.add_trace(
                    go.Scatter(
                        x=[df_cyclic['total'][idx]],
                        y=[prod['oil'].loc['1']-prod['oil'].loc['-1']],
                        name=df_cyclic['start'][idx][:10],
                        mode='markers',
                        marker=dict(color=color, size=10),
                        legendgroup=str(df_cyclic['number'][idx]),
                        showlegend=False,
                    ),
                    row=2, col=1,
                )
            except:
                pass

        fig_cyclic_jobs.update_xaxes(title_text='Month', row=1, col=1)
        fig_cyclic_jobs.update_xaxes(
            title_text='Cyclic Volume (bbls)', row=2, col=1)
        fig_cyclic_jobs.update_yaxes(
            title_text='Incremental Oil (bbls)', row=1, col=1)
        fig_cyclic_jobs.update_yaxes(
            title_text='Incremental Oil (bbls)', row=2, col=1)

        fig_cyclic_jobs.update_layout(
            margin={'l': 0, 't': 0, 'b': 0, 'r': 0},
            font=dict(family='Ubuntu'),
        )

        graphJSON_cyclic_jobs = json.dumps(
            fig_cyclic_jobs, cls=plotly.utils.PlotlyJSONEncoder)
    except:
        graphJSON_cyclic_jobs = None
    client.close()
    return graphJSON_cyclic_jobs


def get_header_oilgas(api):
    client = MongoClient(os.environ['MONGODB_CLIENT'])
    db = client.petroleum
    docs = db.doggr.find(
        {'api': api}, {'cyclic_jobs': 0, 'prodinj': 0, 'crm': 0})
    for x in docs:
        header = dict(x)
    try:
        header.pop('_id')
    except:
        pass
    client.close()
    return header


def get_header_tags_oilgas(tags):
    client = MongoClient(os.environ['MONGODB_CLIENT'])
    db = client.petroleum
    docs = db.doggr.find({'tags': {'$in': tags}}, {
                         'cyclic_jobs': 0, 'prodinj': 0, 'crm': 0})
    headers = []
    for x in docs:
        header = dict(x)
        try:
            header.pop('_id')
        except:
            pass
        headers.append(header)
    client.close()
    return headers


def get_tags_oilgas(api):
    client = MongoClient(os.environ['MONGODB_CLIENT'])
    db = client.petroleum
    docs = db.doggr.find(
        {'api': api}, {'tags': 1})
    for x in docs:
        tags = dict(x)
    taglist = []
    try:
        for val in tags['tags']:
            taglist.append({"id": val, "name": val})
        client.close()
    except:
        pass
    return taglist


def set_tags_oilgas(api, tags):
    client = MongoClient(os.environ['MONGODB_CLIENT'])
    db = client.petroleum
    db.doggr.update({'api': api}, {'$set': {'tags': tags}},
                    upsert=False, multi=False)


def get_graph_oilgas(api, axis):
    client = MongoClient(os.environ['MONGODB_CLIENT'])
    db = client.petroleum
    try:
        df = get_prodinj([api])

        data = [
            go.Scatter(
                x=df['date'],
                y=df['oil'],
                name='oil',
                line=dict(
                    color='#50bf37',
                    shape='spline',
                    smoothing=0.3,
                    width=3
                ),
                mode='lines'
            ),
            go.Scatter(
                x=df['date'],
                y=df['water'],
                name='water',
                line=dict(
                    color='#4286f4',
                    shape='spline',
                    smoothing=0.3,
                    width=3
                ),
                mode='lines'
            ),
            go.Scatter(
                x=df['date'],
                y=df['gas'],
                name='gas',
                line=dict(
                    color='#ef2626',
                    shape='spline',
                    smoothing=0.3,
                    width=3
                ),
                mode='lines'
            ),
            go.Scatter(
                x=df['date'],
                y=df['steam'],
                name='steam',
                line=dict(
                    color='#e32980',
                    shape='spline',
                    smoothing=0.3,
                    width=3
                ),
                mode='lines'
            ),
            go.Scatter(
                x=df['date'],
                y=df['cyclic'],
                name='cyclic',
                line=dict(
                    color='#fcd555',
                    shape='spline',
                    smoothing=0.3,
                    width=3
                ),
                mode='lines'
            ),
            go.Scatter(
                x=df['date'],
                y=df['water_i'],
                name='water_inj',
                line=dict(
                    color='#03b6fc',
                    shape='spline',
                    smoothing=0.3,
                    width=3
                ),
                mode='lines'
            ),
            go.Scatter(
                x=df['date'],
                y=df['gasair'],
                name='gasair',
                line=dict(
                    color='#fc7703',
                    shape='spline',
                    smoothing=0.3,
                    width=3
                ),
                mode='lines'
            ),
            go.Scatter(
                x=df['date'],
                y=df['oilgrav'],
                name='oilgrav',
                visible='legendonly',
                line=dict(
                    color='#81d636',
                    shape='spline',
                    smoothing=0.3,
                    width=3
                ),
                mode='lines'
            ),
            go.Scatter(
                x=df['date'],
                y=df['pcsg'],
                name='pcsg',
                visible='legendonly',
                line=dict(
                    color='#4136d6',
                    shape='spline',
                    smoothing=0.3,
                    width=3
                ),
                mode='lines'
            ),
            go.Scatter(
                x=df['date'],
                y=df['ptbg'],
                name='ptbg',
                visible='legendonly',
                line=dict(
                    color='#7636d6',
                    shape='spline',
                    smoothing=0.3,
                    width=3
                ),
                mode='lines'
            ),
            go.Scatter(
                x=df['date'],
                y=df['btu'],
                name='btu',
                visible='legendonly',
                line=dict(
                    color='#d636d1',
                    shape='spline',
                    smoothing=0.3,
                    width=3
                ),
                mode='lines'
            ),
            go.Scatter(
                x=df['date'],
                y=df['pinjsurf'],
                name='pinjsurf',
                visible='legendonly',
                line=dict(
                    color='#e38f29',
                    shape='spline',
                    smoothing=0.3,
                    width=3
                ),
                mode='lines'
            ),
        ]

        if axis == 'log':
            layout = go.Layout(
                autosize=True,
                font=dict(family='Ubuntu'),
                hovermode='closest',
                hoverlabel=dict(font=dict(family='Ubuntu')),
                showlegend=True,
                legend=dict(orientation='h'),
                yaxis=dict(type='log'),
                uirevision=True,
                margin=dict(r=50, t=30, b=30, l=60, pad=0),
            )
        else:
            layout = go.Layout(
                autosize=True,
                font=dict(family='Ubuntu'),
                hovermode='closest',
                hoverlabel=dict(font=dict(family='Ubuntu')),
                showlegend=True,
                legend=dict(orientation='h'),
                uirevision=True,
                margin=dict(r=50, t=30, b=30, l=60, pad=0),
            )
        graphJSON = json.dumps(dict(data=data, layout=layout),
                               cls=plotly.utils.PlotlyJSONEncoder)
    except:
        graphJSON = None
    client.close()
    return graphJSON


def get_decline_oilgas(api, axis):
    client = MongoClient(os.environ['MONGODB_CLIENT'])
    db = client.petroleum
    try:

        docs = db.doggr.find({'api': str(api)}, {'prodinj': 1, 'decline': 1})
        for x in docs:
            doc = dict(x)
        prodinj = pd.DataFrame(doc['prodinj'])
        decline = pd.DataFrame(doc['decline'])

        start = decline.T['decline_start'].min()
        end = pd.to_datetime(prodinj['date'].max()) + np.timedelta64(48, 'M')

        def model_func(t, qi, d, b):
            if b == 0:
                b = 1e-9
            return qi / ((1 + b * d * t) ** (1/b))

        forecasts = pd.DataFrame(
            index=pd.date_range(
                start=start,
                end=end,
                freq='MS'
            )
        )

        forecasts['date'] = forecasts.index

        try:
            forecasts['oil'] = forecasts.index
            forecasts['oil'] = forecasts['oil'].apply(
                lambda row: model_func(
                    int((
                        (row - pd.to_datetime(decline['oil']['decline_start']))/np.timedelta64(1, 'M'))),
                    decline['oil']['qi'],
                    decline['oil']['d'],
                    decline['oil']['b']
                )
            )
        except:
            pass

        try:
            forecasts['oilcut'] = forecasts.index
            forecasts['oilcut'] = forecasts['oilcut'].apply(
                lambda row: model_func(
                    int((
                        (row - pd.to_datetime(decline['oilcut']['decline_start']))/np.timedelta64(1, 'M'))),
                    decline['oilcut']['qi'],
                    decline['oilcut']['d'],
                    decline['oilcut']['b']
                )
            )
        except:
            pass

        try:
            forecasts['water'] = forecasts.index
            forecasts['water'] = forecasts['water'].apply(
                lambda row: model_func(
                    int((
                        (row - pd.to_datetime(decline['water']['decline_start']))/np.timedelta64(1, 'M'))),
                    decline['water']['qi'],
                    decline['water']['d'],
                    decline['water']['b']
                )
            )
        except:
            pass

        try:
            forecasts['gas'] = forecasts.index
            forecasts['gas'] = forecasts['gas'].apply(
                lambda row: model_func(
                    int((
                        (row - pd.to_datetime(decline['gas']['decline_start']))/np.timedelta64(1, 'M'))),
                    decline['gas']['qi'],
                    decline['gas']['d'],
                    decline['gas']['b']
                )
            )
        except:
            pass

        data = []

        try:
            data.extend(
                [
                    go.Scatter(
                        x=prodinj['date'],
                        y=prodinj['oil'] / 30.45,
                        name='oil',
                        line=dict(
                            color='#50bf37',
                            shape='spline',
                            smoothing=0.3,
                            width=3
                        ),
                        mode='lines'
                    ),
                    go.Scatter(
                        x=forecasts['date'],
                        y=forecasts['oil'],
                        name='oil_fc',
                        line=dict(
                            color='#50bf37',
                            shape='spline',
                            dash='dot',
                            smoothing=0.3,
                            width=3
                        ),
                        mode='lines'
                    ),
                ]
            )
        except:
            pass

        try:
            data.extend(
                [
                    go.Scatter(
                        x=prodinj['date'],
                        y=prodinj['oil'] / (prodinj['water'] + prodinj['oil']),
                        name='oilcut',
                        line=dict(
                            color='#2EF4D6',
                            shape='spline',
                            smoothing=0.3,
                            width=3
                        ),
                        mode='lines'
                    ),
                    go.Scatter(
                        x=forecasts['date'],
                        y=forecasts['oilcut'],
                        name='oilcut_fc',
                        line=dict(
                            color='#2EF4D6',
                            shape='spline',
                            dash='dot',
                            smoothing=0.3,
                            width=3
                        ),
                        mode='lines'
                    ),
                ]
            )
        except:
            pass

        try:
            data.extend(
                [
                    go.Scatter(
                        x=prodinj['date'],
                        y=prodinj['water'] / 30.45,
                        name='water',
                        line=dict(
                            color='#4286f4',
                            shape='spline',
                            smoothing=0.3,
                            width=3
                        ),
                        mode='lines'
                    ),
                    go.Scatter(
                        x=forecasts['date'],
                        y=forecasts['water'],
                        name='water_fc',
                        line=dict(
                            color='#4286f4',
                            shape='spline',
                            dash='dot',
                            smoothing=0.3,
                            width=3
                        ),
                        mode='lines'
                    )
                ]
            )
        except:
            pass

        try:
            data.extend(
                [
                    go.Scatter(
                        x=prodinj['date'],
                        y=prodinj['gas'] / 30.45,
                        name='gas',
                        line=dict(
                            color='#ef2626',
                            shape='spline',
                            smoothing=0.3,
                            width=3
                        ),
                        mode='lines'
                    ),
                    go.Scatter(
                        x=forecasts['date'],
                        y=forecasts['gas'],
                        name='gas_fc',
                        line=dict(
                            color='#ef2626',
                            shape='spline',
                            dash='dot',
                            smoothing=0.3,
                            width=3
                        ),
                        mode='lines'
                    )
                ]
            )
        except:
            pass

        if axis == 'log':
            layout = go.Layout(
                autosize=True,
                font=dict(family='Ubuntu'),
                hovermode='closest',
                hoverlabel=dict(font=dict(family='Ubuntu')),
                showlegend=True,
                legend=dict(orientation='h'),
                yaxis=dict(type='log'),
                uirevision=True,
                margin=dict(r=50, t=30, b=30, l=60, pad=0),
            )
        else:
            layout = go.Layout(
                autosize=True,
                font=dict(family='Ubuntu'),
                hovermode='closest',
                hoverlabel=dict(font=dict(family='Ubuntu')),
                showlegend=True,
                legend=dict(orientation='h'),
                uirevision=True,
                margin=dict(r=50, t=30, b=30, l=60, pad=0),
            )
        graphJSON = json.dumps(dict(data=data, layout=layout),
                               cls=plotly.utils.PlotlyJSONEncoder)
    except:
        graphJSON = None
    client.close()
    return graphJSON


def create_map_oilgas():
    client = MongoClient(os.environ['MONGODB_CLIENT'])
    db = client.petroleum
    df_wells = pd.DataFrame(
        list(db.doggr.find({}, {'field': 1, 'lease': 1, 'well': 1, 'operator': 1, 'api': 1, 'latitude': 1, 'longitude': 1, 'oil_cum': 1, 'water_cum': 1, 'gas_cum': 1, 'wtrstm_cum': 1})))

    df_wells.fillna(0, inplace=True)
    for col in ['oil_cum', 'water_cum', 'gas_cum', 'wtrstm_cum']:
        df_wells[col] = df_wells[col].astype(int)

    df_oil = df_wells[df_wells['oil_cum'] > 0]
    df_water = df_wells[df_wells['water_cum'] > 0]
    df_gas = df_wells[df_wells['gas_cum'] > 0]
    df_wtrstm = df_wells[df_wells['wtrstm_cum'] > 0]

    data = [
        go.Scattermapbox(
            lat=df_water['latitude'].values,
            lon=df_water['longitude'].values,
            mode='markers',
            name='water',
            visible='legendonly',
            text=df_water['water_cum'].values,
            marker=dict(
                size=13,
                color=df_water['water_cum'].values,
                colorbar=dict(
                    title='water',
                    lenmode='fraction',
                    len=0.30,
                ),
                colorscale=scl_wtr,
                cmin=df_water['water_cum'].quantile(
                    0.01),
                cmax=df_water['water_cum'].quantile(
                    0.75),
            )
        ),
        go.Scattermapbox(
            lat=df_oil['latitude'].values,
            lon=df_oil['longitude'].values,
            mode='markers',
            name='oil',
            visible=True,
            text=df_oil['oil_cum'].values,
            marker=dict(
                size=10,
                color=df_oil['oil_cum'].values,
                colorbar=dict(
                    title='oil',
                    lenmode='fraction',
                    len=0.30,
                ),
                colorscale=scl_oil,
                cmin=df_oil['oil_cum'].quantile(0.01),
                cmax=df_oil['oil_cum'].quantile(0.75),
            )
        ),
        go.Scattermapbox(
            lat=df_wtrstm['latitude'].values,
            lon=df_wtrstm['longitude'].values,
            mode='markers',
            name='steam',
            visible='legendonly',
            text=df_wtrstm['wtrstm_cum'].values,
            marker=dict(
                size=7,
                color=df_wtrstm['wtrstm_cum'].values,
                colorbar=dict(
                    title='steam',
                    lenmode='fraction',
                    len=0.30,
                ),
                colorscale=scl_cyc,
                cmin=df_wtrstm['wtrstm_cum'].quantile(
                    0.01),
                cmax=df_wtrstm['wtrstm_cum'].quantile(
                    0.75),
            )
        ),
        go.Scattermapbox(
            lat=df_gas['latitude'].values,
            lon=df_gas['longitude'].values,
            mode='markers',
            name='gas',
            visible='legendonly',
            text=df_gas['gas_cum'].values,
            marker=dict(
                size=7,
                color=df_gas['gas_cum'].values,
                colorbar=dict(
                    title='gas',
                    lenmode='fraction',
                    len=0.30,
                ),
                colorscale=scl_gas,
                cmin=df_gas['gas_cum'].quantile(0.01),
                cmax=df_gas['gas_cum'].quantile(0.75),
            )
        ),
        go.Scattermapbox(
            lat=df_wells['latitude'].values,
            lon=df_wells['longitude'].values,
            mode='markers',
            text=df_wells['api'].values,
            name='wells',
            visible=True,
            marker=dict(
                size=4,
                color='black',
            ),
        ),
    ]

    layout = go.Layout(
        autosize=True,
        font=dict(family='Ubuntu'),
        hovermode='closest',
        hoverlabel=dict(font=dict(family='Ubuntu')),
        uirevision=True,
        showlegend=True,
        legend=dict(orientation='h'),
        margin=dict(r=0, t=0, b=0, l=0, pad=0),
        mapbox=dict(
            bearing=0,
            center=dict(lat=36, lon=-119),
            accesstoken=mapbox_access_token,
            style='mapbox://styles/areed145/ck3j3ab8d0bx31dsp37rshufu',
            pitch=0,
            zoom=5
        )
    )
    graphJSON = json.dumps(dict(data=data, layout=layout),
                           cls=plotly.utils.PlotlyJSONEncoder)

    df_wells = df_wells[['field', 'lease', 'well', 'operator',
                         'api', 'oil_cum', 'water_cum', 'gas_cum', 'wtrstm_cum']]
    client.close()
    return graphJSON, df_wells


def create_map_awc(prop, lat=38, lon=-96, zoom=3, stations='1', infrared='0', radar='0', lightning='0', analysis='0', precip='0', watchwarn='0', temp='0', visible='0'):
    params = {'flight_category': [0, 0, 0, 0, ''],
              'temp_c': [0, 100, 1.8, 32, 'F'],
              'temp_c_var': [0, 100, 1.8, 0, 'F'],
              'temp_c_delta': [0, 100, 1.8, 0, 'F'],
              'dewpoint_c': [0, 100, 1.8, 32, 'F'],
              'dewpoint_c_delta': [0, 100, 1.8, 0, 'F'],
              'temp_dewpoint_spread': [0, 100, 1.8, 0, 'F'],
              'altim_in_hg': [0, 100, 1, 0, 'inHg'],
              'altim_in_hg_var': [0, 100, 1, 0, 'inHg'],
              'altim_in_hg_delta': [0, 100, 1, 0, 'inHg'],
              'wind_dir_degrees': [0, 359, 1, 0, 'degrees'],
              'wind_speed_kt': [0, 100, 1, 0, 'kts'],
              'wind_speed_kt_delta': [0, 100, 1, 0, 'kts'],
              'wind_gust_kt': [0, 100, 1, 0, 'kts'],
              'wind_gust_kt_delta': [0, 100, 1, 0, 'kts'],
              'visibility_statute_mi': [0, 100, 1, 0, 'mi'],
              'cloud_base_ft_agl_0': [0, 10000, 1, 0, 'ft'],
              'cloud_base_ft_agl_0_delta': [0, 10000, 1, 0, 'ft'],
              'sky_cover_0': [0, 100, 1, 0, 'degrees'],
              'precip_in': [0, 10, 1, 0, 'degrees'],
              'elevation_m': [0, 10000, 3.2808, 0, 'ft'],
              'age': [0, 10000, 1, 0, 'minutes'],
              'three_hr_pressure_tendency_mb': [0, 10000, 1, 0, '?'],
              }

    legend = False

    if stations == '1':
        client = MongoClient(os.environ['MONGODB_CLIENT'])
        db = client.wx
        df = pd.DataFrame(list(db.awc.find()))

        if prop == 'temp_dewpoint_spread':
            df['temp_dewpoint_spread'] = df['temp_c'] - df['dewpoint_c']

        if prop == 'age':
            df['age'] = (datetime.utcnow() - df['observation_time']
                         ).astype('timedelta64[m]')

        df.dropna(subset=[prop], inplace=True)

        if prop == 'flight_category':
            df_vfr = df[df['flight_category'] == 'VFR']
            df_mvfr = df[df['flight_category'] == 'MVFR']
            df_ifr = df[df['flight_category'] == 'IFR']
            df_lifr = df[df['flight_category'] == 'LIFR']
            legend = False

            data = [
                go.Scattermapbox(
                    lat=df_vfr['latitude'],
                    lon=df_vfr['longitude'],
                    text=df_vfr['raw_text'],
                    mode='markers',
                    name='VFR',
                    marker=dict(
                        size=10,
                        color='rgb(0,255,0)',
                    )
                ),
                go.Scattermapbox(
                    lat=df_mvfr['latitude'],
                    lon=df_mvfr['longitude'],
                    text=df_mvfr['raw_text'],
                    mode='markers',
                    name='MVFR',
                    marker=dict(
                        size=10,
                        color='rgb(0,0,255)',
                    )
                ),
                go.Scattermapbox(
                    lat=df_ifr['latitude'],
                    lon=df_ifr['longitude'],
                    text=df_ifr['raw_text'],
                    mode='markers',
                    name='IFR',
                    marker=dict(
                        size=10,
                        color='rgb(255,0,0)',
                    )
                ),
                go.Scattermapbox(
                    lat=df_lifr['latitude'],
                    lon=df_lifr['longitude'],
                    text=df_lifr['raw_text'],
                    mode='markers',
                    name='LIFR',
                    marker=dict(
                        size=10,
                        color='rgb(255,127.5,255)',
                    )
                )
            ]
        elif prop == 'sky_cover_0':
            df_clr = df[df['sky_cover_0'] == 'CLR']
            df_few = df[df['sky_cover_0'] == 'FEW']
            df_sct = df[df['sky_cover_0'] == 'SCT']
            df_bkn = df[df['sky_cover_0'] == 'BKN']
            df_ovc = df[df['sky_cover_0'] == 'OVC']
            df_ovx = df[df['sky_cover_0'] == 'OVX']
            legend = True

            data = [
                go.Scattermapbox(
                    lat=df_clr['latitude'],
                    lon=df_clr['longitude'],
                    text=df_clr['raw_text'],
                    mode='markers',
                    name='CLR',
                    marker=dict(
                        size=10,
                        color='rgb(21, 230, 234)',
                    )
                ),
                go.Scattermapbox(
                    lat=df_few['latitude'],
                    lon=df_few['longitude'],
                    text=df_few['raw_text'],
                    mode='markers',
                    name='FEW',
                    marker=dict(
                        size=10,
                        color='rgb(194, 234, 21)',
                    )
                ),
                go.Scattermapbox(
                    lat=df_sct['latitude'],
                    lon=df_sct['longitude'],
                    text=df_sct['raw_text'],
                    mode='markers',
                    name='SCT',
                    marker=dict(
                        size=10,
                        color='rgb(234, 216, 21)',
                    )
                ),
                go.Scattermapbox(
                    lat=df_bkn['latitude'],
                    lon=df_bkn['longitude'],
                    text=df_bkn['raw_text'],
                    mode='markers',
                    name='BKN',
                    marker=dict(
                        size=10,
                        color='rgb(234, 181, 21)',
                    )
                ),
                go.Scattermapbox(
                    lat=df_ovc['latitude'],
                    lon=df_ovc['longitude'],
                    text=df_ovc['raw_text'],
                    mode='markers',
                    name='OVC',
                    marker=dict(
                        size=10,
                        color='rgb(234, 77, 21)',
                    )
                ),
                go.Scattermapbox(
                    lat=df_ovx['latitude'],
                    lon=df_ovx['longitude'],
                    text=df_ovx['raw_text'],
                    mode='markers',
                    name='OVX',
                    marker=dict(
                        size=10,
                        color='rgb(234, 21, 21)',
                    )
                )
            ]
        else:
            if prop == 'wind_dir_degrees':
                cs = cs_circle
                cmin = 0
                cmax = 359
            elif prop == 'visibility_statute_mi':
                cs = cs_rdgn
                cmin = 0
                cmax = 10
            elif prop == 'cloud_base_ft_agl_0':
                cs = cs_rdgn
                cmin = 0
                cmax = 2000
            elif prop == 'age':
                cs = cs_gnrd
                cmin = 0
                cmax = 60
            elif prop == 'temp_dewpoint_spread':
                cs = cs_rdgn
                cmin = 0
                cmax = 5
            elif prop == 'temp_c_delta':
                cs = cs_updown
                cmin = -3
                cmax = 3
            elif prop == 'dewpoint_c_delta':
                cs = cs_updown
                cmin = -3
                cmax = 3
            elif prop == 'altim_in_hg_delta':
                cs = cs_updown
                cmin = -0.03
                cmax = 0.03
            elif prop == 'wind_speed_kt_delta':
                cs = cs_updown
                cmin = -5
                cmax = 5
            elif prop == 'wind_gust_kt_delta':
                cs = cs_updown
                cmin = -5
                cmax = 5
            elif prop == 'cloud_base_ft_agl_0_delta':
                cs = cs_updown
                cmin = -1000
                cmax = 1000
            else:
                cs = cs_normal
                cmin = df[prop].quantile(0.01)
                cmax = df[prop].quantile(0.99)

            data = [
                go.Scattermapbox(
                    lat=df['latitude'],
                    lon=df['longitude'],
                    text=df['raw_text'],
                    mode='markers',
                    marker=dict(
                        size=10,
                        color=params[prop][2] *
                        df[prop] + params[prop][3],
                        colorbar=dict(
                            title=params[prop][4]),
                        colorscale=cs,
                        cmin=params[prop][2] *
                        cmin + params[prop][3],
                        cmax=params[prop][2] *
                        cmax + params[prop][3],
                    )
                )
            ]
        client.close()
    else:
        data = [
            go.Scattermapbox(
                lat=[],
                lon=[],
                mode='markers',
                name='stations',
            )
        ]

    layers = []

    if temp == '1':
        layers.append(
            dict(
                below='traces',
                sourcetype='raster',
                source=[
                    'https://idpgis.ncep.noaa.gov/arcgis/rest/services/NWS_Forecasts_Guidance_Warnings/NDFD_temp/MapServer/export?transparent=true&format=png32&dpi=300&layers=show:1&bbox={bbox-epsg-3857}&bboxSR=3857&imageSR=3857&f=image'
                ]
            )
        )
    if precip == '1':
        layers.append(
            dict(
                below='traces',
                sourcetype='raster',
                source=[
                    'https://idpgis.ncep.noaa.gov/arcgis/rest/services/NWS_Forecasts_Guidance_Warnings/wpc_precip_hazards/MapServer/export?transparent=true&format=png32&dpi=300&layers=show:0&bbox={bbox-epsg-3857}&bboxSR=3857&imageSR=3857&f=image'
                ]
            )
        )
    if watchwarn == '1':
        layers.append(
            dict(
                below='traces',
                sourcetype='raster',
                source=[
                    'https://idpgis.ncep.noaa.gov/arcgis/rest/services/NWS_Forecasts_Guidance_Warnings/watch_warn_adv/MapServer/export?transparent=true&format=png32&dpi=300&layers=show:1&bbox={bbox-epsg-3857}&bboxSR=3857&imageSR=3857&f=image'
                ]
            )
        )
    if infrared == '1':
        layers.append(
            dict(
                below='traces',
                # opacity=0.5,
                sourcetype='raster',
                source=[
                    'https://nowcoast.noaa.gov/arcgis/rest/services/nowcoast/sat_meteo_imagery_time/MapServer/export?transparent=true&format=png32&dpi=300&layers=show:20,8&bbox={bbox-epsg-3857}&bboxSR=3857&imageSR=3857&f=image'
                ]
            )
        )
    if visible == '1':
        layers.append(
            dict(
                below='traces',
                # opacity=0.5,
                sourcetype='raster',
                source=[
                    'https://nowcoast.noaa.gov/arcgis/rest/services/nowcoast/sat_meteo_imagery_time/MapServer/export?transparent=true&format=png32&dpi=300&layers=show:16&bbox={bbox-epsg-3857}&bboxSR=3857&imageSR=3857&f=image'
                ]
            )
        )
    if visible == '1' or infrared == '1':
        layers.append(
            dict(
                below='traces',
                # opacity=0.5,
                sourcetype='raster',
                source=[
                    # 'https://sampleserver6.arcgisonline.com/arcgis/rest/services/USA/MapServer/export?transparent=true&format=png32&dpi=300&layers=show:2&bbox={bbox-epsg-3857}&bboxSR=3857&imageSR=3857&f=image',
                    'https://services.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/export?transparent=true&format=png32&dpi=300&bbox={bbox-epsg-3857}&bboxSR=3857&imageSR=3857&f=image'
                ]
            )
        )
    if radar == '1':
        layers.append(
            dict(
                below='traces',
                sourcetype='raster',
                source=[
                    'https://nowcoast.noaa.gov/arcgis/rest/services/nowcoast/radar_meteo_imagery_nexrad_time/MapServer/export?transparent=true&format=png32&dpi=300&layers=show:0&bbox={bbox-epsg-3857}&bboxSR=3857&imageSR=3857&f=image'
                ]
            )
        )
    if lightning == '1':
        layers.append(
            dict(
                below='traces',
                sourcetype='raster',
                source=[
                    'https://nowcoast.noaa.gov/arcgis/rest/services/nowcoast/sat_meteo_emulated_imagery_lightningstrikedensity_goes_time/MapServer/export?transparent=true&format=png32&dpi=300&layers=show:0&bbox={bbox-epsg-3857}&bboxSR=3857&imageSR=3857&f=image'
                ]
            )
        )
    if analysis == '1':
        layers.append(
            dict(
                sourcetype='raster',
                source=[
                    'https://idpgis.ncep.noaa.gov/arcgis/rest/services/NWS_Forecasts_Guidance_Warnings/natl_fcst_wx_chart/MapServer/export?transparent=true&format=png32&dpi=300&layers=show:1,2&bbox={bbox-epsg-3857}&bboxSR=3857&imageSR=3857&f=image'
                ]
            )
        )

    lat = float(lat)
    lon = float(lon)
    zoom = float(zoom)

    layout = go.Layout(
        autosize=True,
        font=dict(family='Ubuntu'),
        legend=dict(orientation='h'),
        showlegend=legend,
        hovermode='closest',
        hoverlabel=dict(font=dict(family='Ubuntu')),
        uirevision=True,
        margin=dict(r=0, t=0, b=0, l=0, pad=0),
        mapbox=dict(
            bearing=0,
            center=dict(lat=lat, lon=lon),
            accesstoken=mapbox_access_token,
            style='mapbox://styles/areed145/ck3j3ab8d0bx31dsp37rshufu',
            pitch=0,
            layers=layers,
            zoom=zoom))

    graphJSON = json.dumps(dict(data=data, layout=layout),
                           cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


def create_range_aprs(time):
    client = MongoClient(os.environ['MONGODB_CLIENT'])
    lat = 29.780880
    lon = -95.420410

    start, now = get_time_range(time)
    db = client.aprs
    df = pd.DataFrame(list(db.raw.find({
        'script': 'entry',
        'latitude': {'$exists': True, '$ne': None},
        'timestamp_': {'$gt': start, '$lte': now}
    }).sort([('timestamp_', -1)])))
    df['dist'] = np.arccos(np.sin(lat*np.pi/180) * np.sin(df['latitude']*np.pi/180) + np.cos(lat*np.pi/180)
                           * np.cos(df['latitude']*np.pi/180) * np.cos((df['longitude']*np.pi/180) - (lon*np.pi/180))) * 6371

    df['month'] = df['timestamp_'].apply(
        lambda row: str(row.year)+'-'+str(row.month).zfill(2))
    df['dist_'] = np.round(df['dist'] * 1) / 1
    df = df[df['dist'] <= 250]

    c5 = np.array([245/256, 200/256, 66/256, 1])
    c4 = np.array([245/256, 218/256, 66/256, 1])
    c3 = np.array([188/256, 245/256, 66/256, 1])
    c2 = np.array([108/256, 201/256, 46/256, 1])
    c1 = np.array([82/256, 138/256, 45/256, 1])
    c0 = np.array([24/256, 110/256, 45/256, 1])
    total = len(df['month'].unique())
    cm = LinearSegmentedColormap.from_list(
        'custom', [c0, c1, c2, c3, c4, c5], N=total)

    data = []
    for idx, month in enumerate(df['month'].unique()):
        color = rgb2hex(cm(idx/total))
        df2 = df[df['month'] == month]
        df2 = df2.groupby(by='dist_').count()
        data.append(
            go.Scatter(
                x=df2.index,
                y=df2['_id'],
                name=month,
                line=dict(
                    color=color,
                    width=3,
                    shape='spline',
                    smoothing=0.3
                ),
                mode='lines',
            ),
        )

    layout = go.Layout(
        autosize=True,
        hoverlabel=dict(
            font=dict(
                family='Ubuntu'
            )
        ),
        yaxis=dict(
            domain=[0.02, 0.98],
            type='log',
            title='Frequency',
            fixedrange=False,
        ),
        xaxis=dict(
            type='log',
            title='Distance (mi)',
            fixedrange=False,
        ),
        margin=dict(
            r=50,
            t=30,
            b=30,
            l=60,
            pad=0
        ),
        #     showlegend=False,
    )

    graphJSON = json.dumps(dict(data=data, layout=layout),
                           cls=plotly.utils.PlotlyJSONEncoder)
    client.close()
    return graphJSON


def create_map_aprs(script, prop, time):
    params = {'none': [0, 0, 0, 0, ''],
              'altitude': [0, 1000, 3.2808, 0, 'ft'],
              'speed': [0, 100, 0.621371, 0, 'mph'],
              'course': [0, 359, 1, 0, 'degrees'], }
    client = MongoClient(os.environ['MONGODB_CLIENT'])
    db = client.aprs
    start, now = get_time_range(time)
    if script == 'prefix':
        df = pd.DataFrame(list(db.raw.find({
            'script': script,
            'from': 'KK6GPV',
            'latitude': {'$exists': True, '$ne': None},
            'timestamp_': {'$gt': start, '$lte': now}
        }).sort([('timestamp_', -1)])))
    else:
        df = pd.DataFrame(list(db.raw.find({
            'script': script,
            'latitude': {'$exists': True, '$ne': None},
            'timestamp_': {'$gt': start, '$lte': now}
        }).sort([('timestamp_', -1)])))

    if prop == 'none':
        data_map = [
            go.Scattermapbox(
                lat=df['latitude'],
                lon=df['longitude'],
                text=df['raw'],
                mode='markers',
                marker=dict(size=10)
            )
        ]
    else:
        cs = cs_normal
        if prop == 'course':
            cmin = 0
            cmax = 359
            cs = cs_circle
        else:
            cmin = df[prop].quantile(0.01)
            cmax = df[prop].quantile(0.99)
        data_map = [
            go.Scattermapbox(
                lat=df['latitude'],
                lon=df['longitude'],
                text=df['raw'],
                mode='markers',
                marker=dict(
                    size=10,
                    color=params[prop][2] *
                    df[prop] + params[prop][3],
                    colorbar=dict(
                        title=params[prop][4]),
                    colorscale=cs,
                    cmin=params[prop][2] *
                    cmin + params[prop][3],
                    cmax=params[prop][2] *
                    cmax + params[prop][3],
                )
            )
        ]
    layout_map = go.Layout(
        autosize=True,
        font=dict(family='Ubuntu'),
        showlegend=False,
        hovermode='closest',
        hoverlabel=dict(font=dict(family='Ubuntu')),
        uirevision=True,
        margin=dict(r=0, t=0, b=0, l=0, pad=0),
        mapbox=dict(
            bearing=0,
            center=dict(lat=30, lon=-95),
            accesstoken=mapbox_access_token,
            style='mapbox://styles/areed145/ck3j3ab8d0bx31dsp37rshufu',
            pitch=0,
            zoom=6
        )
    )

    data_speed = [
        go.Scatter(
            x=df['timestamp_'],
            y=params['speed'][2] * df['speed'] + params['speed'][3],
            name='Speed (mph)',
            line=dict(
                color='#96F42E',
                width=3,
                shape='spline',
                smoothing=0.3
            ),
            mode='lines'
        ),
    ]

    layout_speed = go.Layout(
        autosize=True,
        height=200,
        hoverlabel=dict(font=dict(family='Ubuntu')),
        yaxis=dict(
            domain=[0.02, 0.98],
            title='Speed (mph)',
            fixedrange=True,
            titlefont=dict(
                color='#96F42E'
            )
        ),
        xaxis=dict(
            type='date',
            fixedrange=False,
            range=[start, now]
        ),
        margin=dict(r=50, t=30, b=30, l=60, pad=0),
        showlegend=False,
    )

    data_alt = [
        go.Scatter(
            x=df['timestamp_'],
            y=params['altitude'][2] * df['altitude'] + params['altitude'][3],
            name='Altitude (ft)',
            line=dict(
                color='#2ED9F4',
                width=3,
                shape='spline',
                smoothing=0.3
            ),
            mode='lines'
        ),
    ]

    layout_alt = go.Layout(
        autosize=True,
        font=dict(family='Ubuntu'),
        hoverlabel=dict(font=dict(family='Ubuntu')),
        height=200,
        yaxis=dict(
            domain=[0.02, 0.98],
            title='Altitude (ft)',
            fixedrange=True,
            titlefont=dict(
                color='#2ED9F4'
            )
        ),
        xaxis=dict(
            type='date',
            fixedrange=False,
            range=[start, now]
        ),
        margin=dict(r=50, t=30, b=30, l=60, pad=0),
        showlegend=False,
    )

    data_course = [
        go.Scatter(
            x=df['timestamp_'],
            y=params['course'][2] * df['course'] + params['course'][3],
            name='Course (degrees)',
            line=dict(
                color='#B02EF4',
                width=3,
                shape='spline',
                smoothing=0.3
            ),
            mode='lines'
        ),
    ]

    layout_course = go.Layout(
        autosize=True,
        font=dict(family='Ubuntu'),
        hoverlabel=dict(font=dict(family='Ubuntu')),
        height=200,
        yaxis=dict(
            domain=[0.02, 0.98],
            title='Course (degrees)',
            fixedrange=True,
            titlefont=dict(
                color='#B02EF4'
            )
        ),
        xaxis=dict(
            type='date',
            fixedrange=False,
            range=[start, now]
        ),
        margin=dict(r=50, t=30, b=30, l=60, pad=0),
        showlegend=False,
    )

    graphJSON_map = json.dumps(dict(data=data_map, layout=layout_map),
                               cls=plotly.utils.PlotlyJSONEncoder)

    graphJSON_speed = json.dumps(dict(data=data_speed, layout=layout_speed),
                                 cls=plotly.utils.PlotlyJSONEncoder)

    graphJSON_alt = json.dumps(dict(data=data_alt, layout=layout_alt),
                               cls=plotly.utils.PlotlyJSONEncoder)

    graphJSON_course = json.dumps(dict(data=data_course, layout=layout_course),
                                  cls=plotly.utils.PlotlyJSONEncoder)

    df['timestamp_'] = df['timestamp_'].apply(
        lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))
    df['latitude'] = np.round(df['latitude'], 3)
    df['longitude'] = np.round(df['longitude'], 3)
    df['speed'] = np.round(df['speed'], 2)
    df['altitude'] = np.round(df['altitude'], 1)
    df['course'] = np.round(df['course'], 1)
    df = df.fillna('')
    rows = []
    for _, row in df.iterrows():
        r = {}
        r['timestamp_'] = row['timestamp_']
        r['from'] = row['from']
        r['to'] = row['to']
        r['via'] = row['via']
        # r['latitude'] = row['latitude']
        # r['longitude'] = row['longitude']
        r['speed'] = row['speed']
        r['altitude'] = row['altitude']
        r['course'] = row['course']
        r['comment'] = row['comment']
        rows.append(r)
    client.close()
    return graphJSON_map, graphJSON_speed, graphJSON_alt, graphJSON_course, rows


def get_aprs_latest():
    client = MongoClient(os.environ['MONGODB_CLIENT'])
    db = client.aprs
    df = pd.DataFrame(list(db.raw.find({
        'script': 'prefix',
        'from': 'KK6GPV',
        'latitude': {'$exists': True, '$ne': None}
    }).sort([('timestamp_', -1)]).limit(1)))
    last = {}
    last['timestamp_'] = df['timestamp_'].values[0]
    last['hours_ago'] = (datetime.utcnow() - pd.to_datetime(df['timestamp_'].values[0]))/np.timedelta64(1, 'H')
    last['latitude'] = df['latitude'].values[0]
    last['longitude'] = df['longitude'].values[0]
    return last


def get_wx_latest(sid):
    client = MongoClient(os.environ['MONGODB_CLIENT'])
    db = client.wx
    wx = list(db.raw.find({'station_id': sid}).sort(
        [('observation_time_rfc822', -1)]).limit(1))[0]
    wx.pop('_id')
    client.close()
    return wx


def create_wx_figs(time, sid):
    start, now = get_time_range(time)
    client = MongoClient(os.environ['MONGODB_CLIENT'])
    db = client.wx
    df_wx_raw = pd.DataFrame(list(db.raw.find({
        'station_id': sid,
        'observation_time_rfc822': {
            '$gt': start,
            '$lte': now
        }}).sort([('observation_time_rfc822', -1)])))
    df_wx_raw.index = df_wx_raw['observation_time_rfc822']
    # df_wx_raw = df_wx_raw.tz_localize('UTC').tz_convert('US/Central')

    for col in df_wx_raw.columns:
        try:
            df_wx_raw.loc[df_wx_raw[col] < -50, col] = pd.np.nan
        except:
            pass

    df_wx_raw['cloudbase'] = (
        (df_wx_raw['temp_f'] - df_wx_raw['dewpoint_f']) / 4.4) * 1000 + 50
    df_wx_raw.loc[df_wx_raw['pressure_in'] < 0, 'pressure_in'] = pd.np.nan

    # df_wx_raw2 = df_wx_raw.resample('5T').mean().interpolate()
    # df_wx_raw2['dat'] = df_wx_raw2.index
    # df_wx_raw2['temp_delta'] = df_wx_raw2.temp_f.diff()
    # df_wx_raw2['precip_today_delta'] = df_wx_raw2.precip_today_in.diff()
    # df_wx_raw2.loc[df_wx_raw2['precip_today_delta'] < 0, 'precip_today_delta'] = 0
    # df_wx_raw2['precip_cum_in'] = df_wx_raw2.precip_today_delta.cumsum()
    # df_wx_raw2['pres_delta'] = df_wx_raw2.pressure_in.diff()
    # df_wx_raw2['dat_delta'] = df_wx_raw2.dat.diff().dt.seconds / 360
    # df_wx_raw2['dTdt'] = df_wx_raw2['temp_delta'] / df_wx_raw2['dat_delta']
    # df_wx_raw2['dPdt'] = df_wx_raw2['pres_delta'] / df_wx_raw2['dat_delta']
    # df_wx_raw3 = df_wx_raw2.drop(columns=['dat'])
    # df_wx_raw3 = df_wx_raw3.rolling(20*3).mean().add_suffix('_roll')
    # df_wx_raw = df_wx_raw2.join(df_wx_raw3)

    df_wx_raw['dat'] = df_wx_raw.index
    df_wx_raw.sort_values(by='dat', inplace=True)
    df_wx_raw['temp_delta'] = df_wx_raw.temp_f.diff()
    df_wx_raw['precip_today_delta'] = df_wx_raw.precip_today_in.diff()
    df_wx_raw.loc[df_wx_raw['precip_today_delta']
                  < 0, 'precip_today_delta'] = 0
    df_wx_raw['precip_cum_in'] = df_wx_raw.precip_today_delta.cumsum()
    df_wx_raw['pres_delta'] = df_wx_raw.pressure_in.diff()
    df_wx_raw['dat_delta'] = df_wx_raw.dat.diff().dt.seconds / 360
    df_wx_raw['dTdt'] = df_wx_raw['temp_delta'] / df_wx_raw['dat_delta']
    df_wx_raw['dPdt'] = df_wx_raw['pres_delta'] / df_wx_raw['dat_delta']

    df_wx_raw['date'] = df_wx_raw.index.date
    df_wx_raw['hour'] = df_wx_raw.index.hour

    df_wx_raw.loc[df_wx_raw['wind_mph'] == 0, 'wind_cat'] = 'calm'
    df_wx_raw.loc[df_wx_raw['wind_mph'] > 0, 'wind_cat'] = '0-1'
    df_wx_raw.loc[df_wx_raw['wind_mph'] > 1, 'wind_cat'] = '1-2'
    df_wx_raw.loc[df_wx_raw['wind_mph'] > 2, 'wind_cat'] = '2-5'
    df_wx_raw.loc[df_wx_raw['wind_mph'] > 5, 'wind_cat'] = '5-10'
    df_wx_raw.loc[df_wx_raw['wind_mph'] > 10, 'wind_cat'] = '>10'

    df_wx_raw['wind_degrees_cat'] = np.floor(
        df_wx_raw['wind_degrees'] / 15) * 15
    df_wx_raw.loc[df_wx_raw['wind_degrees_cat'] == 360, 'wind_degrees_cat'] = 0
    df_wx_raw['wind_degrees_cat'] = df_wx_raw['wind_degrees_cat'].fillna(
        0).astype(int).astype(str)

    df_wx_raw.loc[df_wx_raw['wind_mph'] == 0, 'wind_degrees'] = pd.np.nan

    wind = df_wx_raw[['wind_cat', 'wind_degrees_cat']]
    wind.loc[:, 'count'] = 1
    # wind['count'] = 1
    ct = len(wind)
    wind = pd.pivot_table(wind, values='count', index=[
        'wind_degrees_cat'], columns=['wind_cat'], aggfunc=np.sum)
    ix = np.arange(0, 360, 5)
    col = ['calm', '0-1', '1-2', '2-5', '5-10', '>10']
    wind_temp = pd.DataFrame(data=0, index=ix, columns=col)
    for i in ix:
        for j in col:
            try:
                wind_temp.loc[i, j] = wind.loc[str(i), j]
            except:
                pass
    wind_temp = wind_temp.fillna(0)
    wind_temp['calm'] = wind_temp['calm'].mean()
    for col in range(len(wind_temp.columns)):
        try:
            wind_temp.iloc[:, col] = wind_temp.iloc[:, col] + \
                wind_temp.iloc[:, col-1]
        except:
            pass
    wind_temp = np.round(wind_temp / ct * 100, 2)
    wind_temp['wind_cat'] = wind_temp.index

    dt_min = df_wx_raw.index.min()
    dt_max = df_wx_raw.index.max()

    td_max = max(df_wx_raw['temp_f'].max(), df_wx_raw['dewpoint_f'].max()) + 1
    td_min = min(df_wx_raw['temp_f'].min(), df_wx_raw['dewpoint_f'].min()) - 1

    data_td = [
        go.Scatter(
            x=df_wx_raw.index,
            y=df_wx_raw['temp_f'],
            name='Temperature (F)',
            line=dict(
                color='rgb(255, 95, 63)',
                width=3,
                shape='spline',
                smoothing=0.3
            ),
            xaxis='x',
            yaxis='y',
            mode='lines'
        ),
        go.Scatter(
            x=df_wx_raw.index,
            y=df_wx_raw['heat_index_f'],
            name='Heat Index (F)',
            line=dict(
                color='#F42ED0',
                width=3,
                shape='spline',
                smoothing=0.3
            ),
            xaxis='x',
            yaxis='y',
            mode='lines'
        ),
        go.Scatter(
            x=df_wx_raw.index,
            y=df_wx_raw['windchill_f'],
            name='Windchill (F)',
            line=dict(
                color='#2EE8F4',
                width=3,
                shape='spline',
                smoothing=0.3
            ),
            xaxis='x',
            yaxis='y',
            mode='lines'
        ),
        go.Scatter(
            x=df_wx_raw.index,
            y=df_wx_raw['dewpoint_f'],
            name='Dewpoint (F)',
            line=dict(
                color='rgb(63, 127, 255)',
                width=3,
                shape='spline',
                smoothing=0.3),
            xaxis='x',
            yaxis='y2',
            mode='lines'
        ),
    ]

    layout_td = go.Layout(
        autosize=True,
        font=dict(family='Ubuntu'),
        hoverlabel=dict(font=dict(family='Ubuntu')),
        height=200,
        yaxis=dict(
            domain=[0.02, 0.98],
            title='Temperature (F)',
            range=[td_min, td_max],
            fixedrange=True,
            titlefont=dict(
                family='Ubuntu',
                color='rgb(255, 95, 63)'
            )
        ),
        yaxis2=dict(
            domain=[0.02, 0.98],
            title='Dewpoint (F)',
            overlaying='y',
            side='right',
            range=[td_min, td_max],
            fixedrange=True,
            titlefont=dict(
                family='Ubuntu',
                color='rgb(63, 127, 255)')
        ),
        xaxis=dict(type='date',
                   # fixedrange=True,
                   range=[dt_min, dt_max],
                   ),
        margin=dict(r=50, t=30, b=30, l=60, pad=0),
        showlegend=False,
    )

    data_pr = [
        go.Scatter(
            x=df_wx_raw.index,
            y=df_wx_raw['pressure_in'],
            name='Pressure (inHg)',
            line=dict(
                color='rgb(255, 127, 63)',
                width=3,
                shape='spline',
                smoothing=0.3
            ),
            xaxis='x',
            yaxis='y',
            mode='lines'
        ),
        go.Scatter(
            x=df_wx_raw.index,
            y=df_wx_raw['relative_humidity'],
            name='Humidity (%)',
            line=dict(
                color='rgb(127, 255, 63)',
                width=3,
                shape='spline',
                smoothing=0.3
            ),
            xaxis='x',
            yaxis='y2',
            mode='lines'
        ),
    ]

    layout_pr = go.Layout(
        autosize=True,
        height=200,
        font=dict(family='Ubuntu'),
        hoverlabel=dict(font=dict(family='Ubuntu')),
        yaxis=dict(
            domain=[0.02, 0.98],
            title='Pressure (inHg)',
            # range=[0,120],
            fixedrange=True,
            titlefont=dict(
                family='Ubuntu',
                color='rgb(255, 127, 63)')
        ),
        yaxis2=dict(
            domain=[0.02, 0.98],
            title='Humidity (%)',
            overlaying='y',
            side='right',
            # range=[0,120],
            fixedrange=True,
            titlefont=dict(
                family='Ubuntu', color='rgb(127, 255, 63)')
        ),
        xaxis=dict(
            type='date',
            # fixedrange=True,
            range=[dt_min, dt_max],
        ),
        margin=dict(r=50, t=30, b=30, l=60, pad=0),
        showlegend=False,
    )

    data_pc = [
        go.Scatter(
            x=df_wx_raw.index,
            y=df_wx_raw['precip_1hr_in'],
            name='Precip (in/hr)',
            line=dict(
                color='rgb(31, 190, 255)',
                width=3,
                shape='spline',
                smoothing=0.3
            ),
            xaxis='x',
            yaxis='y',
            mode='lines'
        ),
        go.Scatter(
            x=df_wx_raw.index,
            y=df_wx_raw['precip_cum_in'],
            name='Precip Cumulative (in)',
            line=dict(
                color='rgb(63, 255, 255)',
                width=3,
                shape='spline',
                smoothing=0.3
            ),
            xaxis='x',
            yaxis='y2',
            mode='lines'
        ),
    ]

    layout_pc = go.Layout(
        autosize=True,
        height=200,
        font=dict(family='Ubuntu'),
        hoverlabel=dict(font=dict(family='Ubuntu')),
        yaxis=dict(
            domain=[0.02, 0.98],
            title='Precip (in/hr)',
            # range=[0,120],
            fixedrange=True,
            titlefont=dict(
                family='Ubuntu',
                color='rgb(31, 190, 255)')
        ),
        yaxis2=dict(
            domain=[0.02, 0.98],
            title='Precip Cumulative (in)',
            overlaying='y',
            side='right',
            # range=[0,120],
            fixedrange=True,
            titlefont=dict(
                family='Ubuntu',
                color='rgb(63, 255, 255)')
        ),
        xaxis=dict(
            type='date',
            # fixedrange=True,
            range=[dt_min, dt_max],
        ),
        margin=dict(r=50, t=30, b=30, l=60, pad=0),
        showlegend=False,
    )

    data_cb = [
        go.Scatter(
            x=df_wx_raw.index,
            y=df_wx_raw['cloudbase'],
            name='Minimum Cloudbase (ft)',
            line=dict(
                color='rgb(90, 66, 245)',
                width=3,
                shape='spline',
                smoothing=0.3
            ),
            xaxis='x',
            yaxis='y',
            mode='lines'
        ),
    ]

    layout_cb = go.Layout(
        autosize=True,
        height=200,
        font=dict(family='Ubuntu'),
        hoverlabel=dict(font=dict(family='Ubuntu')),
        yaxis=dict(
            domain=[0.02, 0.98],
            title='Minimum Cloudbase (ft)',
            # range=[0,120],
            fixedrange=True,
            titlefont=dict(
                family='Ubuntu',
                color='rgb(90, 66, 245)')
        ),
        xaxis=dict(
            type='date',
            # fixedrange=True,
            range=[dt_min, dt_max],
        ),
        margin=dict(r=50, t=30, b=30, l=60, pad=0),
        showlegend=False,
    )

    data_wd = [
        go.Scatter(
            x=df_wx_raw.index,
            y=df_wx_raw['wind_degrees'],
            name='Wind Direction (degrees)',
            marker=dict(
                color='rgb(190, 63, 255)',
                size=8,
                symbol='x'
            ),
            xaxis='x',
            yaxis='y',
            mode='markers'
        ),
        go.Scatter(
            x=df_wx_raw.index,
            y=df_wx_raw['wind_gust_mph'] * 0.869,
            name='Wind Gust (kts)',
            line=dict(
                color='rgb(31, 190, 15)',
                width=3,
                shape='spline',
                smoothing=0.3
            ),
            xaxis='x',
            yaxis='y2',
            mode='lines'
        ),
        go.Scatter(
            x=df_wx_raw.index,
            y=df_wx_raw['wind_mph'] * 0.869,
            name='Wind Speed (kts)',
            line=dict(
                color='rgb(127, 255, 31)',
                width=3,
                shape='spline',
                smoothing=0.3
            ),
            xaxis='x',
            yaxis='y2',
            mode='lines'
        ),
    ]

    layout_wd = go.Layout(
        autosize=True,
        height=200,
        font=dict(family='Ubuntu'),
        hoverlabel=dict(font=dict(family='Ubuntu')),
        yaxis=dict(
            domain=[0.02, 0.98],
            title='Wind Direction (degrees)',
            range=[0, 360],
            fixedrange=True,
            titlefont=dict(
                family='Ubuntu',
                color='rgb(190, 63, 255)'
            )
        ),
        yaxis2=dict(
            domain=[0.02, 0.98],
            title='Wind Speed / Gust (kts)',
            overlaying='y',
            side='right',
            range=[
                0, df_wx_raw['wind_gust_mph'].max() * 0.869],
            fixedrange=True,
            titlefont=dict(
                family='Ubuntu',
                color='rgb(127, 255, 31)'
            )
        ),
        xaxis=dict(
            type='date',
            # fixedrange=True,
            range=[dt_min, dt_max],
        ),
        margin=dict(r=50, t=30, b=30, l=60, pad=0),
        showlegend=False,
    )

    data_su = [
        go.Scatter(
            x=df_wx_raw.index,
            y=df_wx_raw['solar_radiation'],
            name='Solar Radiation (W/m<sup>2</sup>)',
            line=dict(
                color='rgb(255, 63, 127)',
                width=3,
                shape='spline',
                smoothing=0.3
            ),
            xaxis='x',
            yaxis='y',
            mode='lines'),
        go.Scatter(
            x=df_wx_raw.index,
            y=df_wx_raw['UV'],
            name='UV',
            line=dict(
                color='rgb(255, 190, 63)',
                width=3,
                shape='spline',
                smoothing=0.3
            ),
            xaxis='x',
            yaxis='y2',
            mode='lines'),
    ]

    layout_su = go.Layout(
        autosize=True,
        height=200,
        font=dict(family='Ubuntu'),
        hoverlabel=dict(font=dict(family='Ubuntu')),
        yaxis=dict(
            domain=[0.02, 0.98],
            title='Solar Radiation (W/m<sup>2</sup>)',
            # range=[0,120],
            fixedrange=True,
            titlefont=dict(
                family='Ubuntu', color='rgb(255, 63, 127)')
        ),
        yaxis2=dict(
            domain=[0.02, 0.98],
            title='UV',
            overlaying='y',
            side='right',
            # range=[0,120],
            fixedrange=True,
            titlefont=dict(
                family='Ubuntu', color='rgb(255, 190, 63)')
        ),
        xaxis=dict(
            type='date',
            # fixedrange=True,
            range=[dt_min, dt_max],
        ),
        margin=dict(r=50, t=30, b=30, l=60, pad=0),
        showlegend=False,
    )

    t1 = go.Barpolar(
        r=wind_temp['>10'],
        theta=wind_temp['wind_cat'],
        name='>10 mph',
        width=10,
        base=0,
        marker=dict(
            color='#ffff00',
            line=dict(color='#ffff00')
        ),
    )
    t2 = go.Barpolar(
        r=wind_temp['5-10'],
        theta=wind_temp['wind_cat'],
        name='5-10 mph',
        width=10,
        base=0,
        marker=dict(color='#ffcc00',
                    line=dict(color='#ffcc00')
                    ),
    )
    t3 = go.Barpolar(
        r=wind_temp['2-5'],
        theta=wind_temp['wind_cat'],
        name='2-5 mph',
        width=10,
        base=0,
        marker=dict(
            color='#bfff00',
            line=dict(color='#bfff00')
        ),
    )
    t4 = go.Barpolar(
        r=wind_temp['1-2'],
        theta=wind_temp['wind_cat'],
        name='1-2 mph',
        width=10,
        base=0,
        marker=dict(
            color='#00cc00',
            line=dict(color='#00cc00')
        ),
    )
    t5 = go.Barpolar(
        r=wind_temp['0-1'],
        theta=wind_temp['wind_cat'],
        name='0-1 mph', width=10,
        base=0,
        marker=dict(
            color='#009999',
            line=dict(color='#009999')
        ),
    )
    t6 = go.Barpolar(
        r=wind_temp['calm'],
        theta=wind_temp['wind_cat'],
        name='calm',
        width=10,
        base=0,
        marker=dict(
            color='#3366ff',
            line=dict(color='#3366ff')
        ),
    )

    data_wr = [t1, t2, t3, t4, t5, t6]

    layout_wr = go.Layout(
        font=dict(family='Ubuntu'),
        hoverlabel=dict(font=dict(family='Ubuntu')),
        polar=dict(
            radialaxis=dict(
                # visible = False,
                showline=False,
                showticklabels=False,
                ticks='',
                range=[0, wind_temp['>10'].max()],
            ),
            angularaxis=dict(
                rotation=90,
                direction="clockwise",
            )
        ),
    )

    graphJSON_td = json.dumps(dict(data=data_td, layout=layout_td),
                              cls=plotly.utils.PlotlyJSONEncoder)

    graphJSON_pr = json.dumps(dict(data=data_pr, layout=layout_pr),
                              cls=plotly.utils.PlotlyJSONEncoder)

    graphJSON_pc = json.dumps(dict(data=data_pc, layout=layout_pc),
                              cls=plotly.utils.PlotlyJSONEncoder)

    graphJSON_cb = json.dumps(dict(data=data_cb, layout=layout_cb),
                              cls=plotly.utils.PlotlyJSONEncoder)

    graphJSON_wd = json.dumps(dict(data=data_wd, layout=layout_wd),
                              cls=plotly.utils.PlotlyJSONEncoder)

    graphJSON_su = json.dumps(dict(data=data_su, layout=layout_su),
                              cls=plotly.utils.PlotlyJSONEncoder)

    graphJSON_wr = json.dumps(dict(data=data_wr, layout=layout_wr),
                              cls=plotly.utils.PlotlyJSONEncoder)

    graphJSON_thp = create_3d_plot(df_wx_raw, 'temp_f', 'dewpoint_f', 'relative_humidity', cs_normal, 'Temperature (F)',
                                   'Dewpoint (F)', 'Humidity (%)', 'rgb(255, 95, 63)', 'rgb(255, 127, 63)', 'rgb(63, 127, 255)')

    client.close()
    return graphJSON_td, graphJSON_pr, graphJSON_cb, graphJSON_pc, graphJSON_wd, graphJSON_su, graphJSON_wr, graphJSON_thp


def get_image(name):
    client = MongoClient(os.environ['MONGODB_CLIENT'])
    db = client.wx_gfx
    fs = gridfs.GridFS(db)
    file = fs.find_one({"filename": name})
    img = fs.get(file._id).read()
    img = base64.b64decode(img)
    img = img[img.find(b'<svg'):]
    img = re.sub(b'height="\d*.\d*pt"', b'height="100%"', img)
    img = re.sub(b'width="\d*.\d*pt"', b'width="100%"', img)
    client.close()
    return img
