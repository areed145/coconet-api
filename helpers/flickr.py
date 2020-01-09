#from __future__ import print_function

import flickr_api as f
import pickle
from pymongo import MongoClient
import os

client = MongoClient(os.environ['MONGODB_CLIENT'])
db = client.flickr


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
                {'caption': gal['title'] + ' - ' + str(gal['count_photos']),
                 'thumb': gal['primary'],
                 'kk6gpv_link': gal['kk6gpv_link']},
            )
            idx += 1
        else:
            frames.append(
                {'caption': gal['title'] + ' - ' + str(gal['count_photos']),
                 'thumb': gal['primary'],
                 'kk6gpv_link': gal['kk6gpv_link']},
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
    idx = 1
    for ph in gal[0]['photos']:
        if (idx/width) != (idx//width):
            frames.append(
                {'thumb': gal[0]['photos'][ph]['thumb'],
                 'kk6gpv_link': '/galleries/'+id+'/'+ph},
            )
            idx += 1
        else:
            frames.append(
                {'thumb': gal[0]['photos'][ph]['thumb'],
                 'kk6gpv_link': '/galleries/'+id+'/'+ph},
            )
            rows.append(frames)
            frames = []
            idx = 1
    rows.append(frames)
    return rows
