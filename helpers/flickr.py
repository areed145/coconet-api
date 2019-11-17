#from __future__ import print_function

import flickr_api as f
import pickle

f.set_keys(api_key='77a2ae7ea816558f00e4dd32249be54e',
           api_secret='2267640a7461db21')
f.set_auth_handler('helpers/auth')
username = '- Adam Reeder -'
u = f.Person.findByUserName(username)


def get_gals():
    ps = u.getPhotosets()

    gals = {}
    for p in ps:
        pid = p.id
        title = p.title
        count_photos = p.count_photos
        count_views = p.count_views
        primary = 'https://live.staticflickr.com/' + \
            p.server+'/'+p.primary+'_'+p.secret+'_q_d.jpg'
        flickr_link = 'https://www.flickr.com/photos/adamreeder/albums/'+p.id
        kk6gpv_link = '/galleries/'+p.id
        photos = {}
        phs = p.getPhotos()
        for ph in phs:
            photos[ph.id] = {
                'thumb': 'https://live.staticflickr.com/'+ph.server+'/'+ph.id+'_'+ph.secret+'_q_d.jpg',
                'large': 'https://live.staticflickr.com/'+ph.server+'/'+ph.id+'_'+ph.secret+'_b.jpg'
            }
        gals[pid] = {
            'id': pid,
            'title': title,
            'count_photos': count_photos,
            'count_views': count_views,
            'primary': primary,
            'flickr_link': flickr_link,
            'kk6gpv_link': kk6gpv_link,
            'photos': photos
        }
    g = open('static/gals', 'wb')
    pickle.dump(gals, g)
    print('galleries updated')
    return gals


def load_gals():
    g = open('static/gals', 'rb')
    gals = pickle.load(g)
    return gals


def get_gal_rows(width):
    g = open('static/gals', 'rb')
    gals = pickle.load(g)
    rows = []
    frames = []
    idx = 1
    for gal in gals:
        if (idx/width) != (idx//width):
            frames.append(
                {'caption': gals[gal]['title'] + ' - ' + str(gals[gal]['count_photos']),
                 'thumb': gals[gal]['primary'],
                 'kk6gpv_link': gals[gal]['kk6gpv_link']},
            )
            idx += 1
        else:
            frames.append(
                {'caption': gals[gal]['title'] + ' - ' + str(gals[gal]['count_photos']),
                 'thumb': gals[gal]['primary'],
                 'kk6gpv_link': gals[gal]['kk6gpv_link']},
            )
            rows.append(frames)
            frames = []
            idx = 1
    rows.append(frames)
    return rows


def get_photo_rows(id, width):
    g = open('static/gals', 'rb')
    gals = pickle.load(g)
    rows = []
    frames = []
    idx = 1
    for ph in gals[id]['photos']:
        if (idx/width) != (idx//width):
            frames.append(
                {'thumb': gals[id]['photos'][ph]['thumb'],
                 'kk6gpv_link': '/galleries/'+id+'/'+ph},
            )
            idx += 1
        else:
            frames.append(
                {'thumb': gals[id]['photos'][ph]['thumb'],
                 'kk6gpv_link': '/galleries/'+id+'/'+ph},
            )
            rows.append(frames)
            frames = []
            idx = 1
    rows.append(frames)
    return rows, gals
