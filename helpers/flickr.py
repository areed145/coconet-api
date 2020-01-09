#from __future__ import print_function

import flickr_api as f
import pickle
from pymongo import MongoClient
import os
import numpy as np
import plotly
import plotly.graph_objs as go
import json

client = MongoClient(os.environ['MONGODB_CLIENT'])
db = client.flickr

mapbox_access_token = os.environ['MAPBOX_TOKEN']


def load_gals():
    gals = list(db.galleries.find({}, {"photos": 0}))
    return gals


def get_gal_rows(width):
    gals = list(db.galleries.find({}, {"photos": 0}))
    rows = []
    frames = []
    idx = 1
    for gal in gals:
        if (idx/width) != (idx//width):
            frames.append(
                {
                    'caption': gal['title'] + ' - ' + str(gal['count_photos']),
                    'thumb': gal['primary'],
                    'kk6gpv_link': '/gallery/'+gal['id']
                },
            )
            idx += 1
        else:
            frames.append(
                {
                    'caption': gal['title'] + ' - ' + str(gal['count_photos']),
                    'thumb': gal['primary'],
                    'kk6gpv_link': '/gallery/'+gal['id']
                },
            )
            rows.append(frames)
            frames = []
            idx = 1
    rows.append(frames)
    return rows


def get_photo_rows(id, width):
    gal = list(db.galleries.find({'id': id}))
    rows = []
    frames = []
    lats = []
    lons = []
    idx = 1
    for phid in gal[0]['photos']:
        if (idx/width) != (idx//width):
            frames.append(
                {
                    'thumb': gal[0]['photos'][phid]['thumb'],
                    'kk6gpv_link': '/photo/'+phid
                },
            )
            try:
                lats.append(float(gal[0]['photos'][phid]['latitude']))
                lons.append(float(gal[0]['photos'][phid]['longitude']))
            except:
                pass
            idx += 1
        else:
            frames.append(
                {
                    'thumb': gal[0]['photos'][phid]['thumb'],
                    'kk6gpv_link': '/photo/'+phid
                },
            )
            try:
                lats.append(float(gal[0]['photos'][phid]['latitude']))
                lons.append(float(gal[0]['photos'][phid]['longitude']))
            except:
                pass
            rows.append(frames)
            frames = []
            idx = 1
    rows.append(frames)

    lat_c = np.array(lats).mean()
    lon_c = np.array(lons).mean()

    data = [
        go.Scattermapbox(
            lat=lats,
            lon=lons,
            mode='markers',
            marker=dict(size=10)
        )
    ]
    layout = go.Layout(
        autosize=True,
        font=dict(family='Ubuntu'),
        showlegend=False,
        hovermode='closest',
        hoverlabel=dict(
            font=dict(
                family='Ubuntu'
            )
        ),
        uirevision=True,
        margin=dict(r=0, t=0, b=0, l=0, pad=0),
        mapbox=dict(
            bearing=0,
            center=dict(lat=lat_c, lon=lon_c),
            accesstoken=mapbox_access_token,
            style='mapbox://styles/areed145/ck3j3ab8d0bx31dsp37rshufu',
            pitch=0,
            zoom=2
        )
    )

    graphJSON = json.dumps(dict(data=data, layout=layout),
                           cls=plotly.utils.PlotlyJSONEncoder)
    return rows, graphJSON, gal['title'], gal['count_photos'], gal['count_views']


def get_photo(id):
    image = list(db.photos.find({'id': id}))[0]
    image.pop('_id')
    return image
