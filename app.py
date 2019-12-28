import base64
import os
import time
import atexit
import json
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template, request, session, g, redirect, render_template_string, make_response
from flask_cors import CORS
from helpers import figs, flickr
from helpers.blog import Database, Blog, Post, User
from micawber.providers import bootstrap_basic
from micawber.contrib.mcflask import add_oembed_filters
from werkzeug.middleware.proxy_fix import ProxyFix
from pymongo import MongoClient
from helpers.tracker import TrackUsage
from helpers.tracker.storage.mongo import MongoPiggybackStorage
from flask_caching import Cache
import json
import feather
import pandas as pd

app = Flask(__name__)
CORS(app)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=0, x_proto=1)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

sid = os.environ['SID']

client = MongoClient(os.environ['MONGODB_CLIENT'])
db = client.coconut_barometer
stats = db.stats

app.secret_key = "secret"

oembed_providers = bootstrap_basic()
add_oembed_filters(app, oembed_providers)

times = dict(m_5='5m', h_1='1h', h_6='6h', d_1='1d',
             d_2='2d', d_7='7d', d_30='30d')

app.config['TRACK_USAGE_USE_FREEGEOIP'] = True
app.config['TRACK_USAGE_INCLUDE_OR_EXCLUDE_VIEWS'] = 'include'
app.config['TRACK_USAGE_COOKIE'] = True

t = TrackUsage(app, [MongoPiggybackStorage(stats)])

sched = BackgroundScheduler(daemon=True)
sched.add_job(flickr.get_gals, 'interval', hours=1)
sched.start()


def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()


@app.before_first_request
def initialize_database():
    Database.initialize()


@cache.cached(timeout=60)
@t.include
@app.route('/')
def index():
    g.track_var['page'] = 'home'
    wx = figs.get_wx_latest(sid)
    wxmap = figs.create_map_awc(
        'flight_category', 29.780880, -95.420410, zoom=6, radar="1", lightning="1")
    return render_template('index.html', wx=wx, wxmap=wxmap)


@cache.cached(timeout=60)
@t.include
@app.route('/weather/aviation')
def awc():
    g.track_var['page'] = 'weather_aviation'
    prop_awc = 'flight_category'
    map_awc = figs.create_map_awc(prop_awc)
    return render_template('weather_aviation.html', plot=map_awc)


@t.include
@app.route('/station/live')
def station_live():
    g.track_var['page'] = 'station_live'
    wx = figs.get_wx_latest(sid)
    wxmap = figs.create_map_awc(
        'flight_category', 29.780880, -95.420410, zoom=6, radar="1", lightning="1")
    return render_template('station_live.html', wx=wx, wxmap=wxmap)


@cache.cached(timeout=60)
@t.include
@app.route('/station/history')
def station_history():
    g.track_var['page'] = 'station_history'
    time_int = 'd_1'
    fig_td, fig_pr, fig_cb, fig_pc, fig_wd, fig_su, fig_wr, fig_thp = figs.create_wx_figs(
        time_int, sid)
    return render_template('station_history.html', times=times, fig_td=fig_td, fig_pr=fig_pr, fig_cb=fig_cb, fig_pc=fig_pc, fig_wd=fig_wd, fig_su=fig_su, fig_wr=fig_wr, fig_thp=fig_thp)


@cache.cached(timeout=60)
@t.include
@app.route('/station/info')
def station_info():
    g.track_var['page'] = 'station_info'
    return render_template('station_info.html')


@cache.cached(timeout=60)
@t.include
@app.route('/weather/blips')
def blips():
    g.track_var['page'] = 'blips'
    return render_template('blips.html')


@cache.cached(timeout=60)
@t.include
@app.route('/weather/soundings')
def soundings():
    g.track_var['page'] = 'soundings'
    img = figs.get_image('OAK')
    return render_template('soundings.html', img=img)


@cache.cached(timeout=60)
@t.include
@app.route('/iot')
def iot():
    g.track_var['page'] = 'iot'
    sensor_iot = ['sensor.load_1m']
    time_int = 'm_5'
    graph_iot = figs.create_graph_iot(sensor_iot, time_int)
    return render_template('iot.html', times=times, plot=graph_iot)


@cache.cached(timeout=6)
@t.include
@app.route('/aprs_<type_aprs>')
def aprs(type_aprs):
    g.track_var['page'] = type_aprs
    if type_aprs == 'info':
        return render_template('aprs_info.html')
    else:
        prop_aprs = 'speed'
        if type_aprs == 'radius':
            time_int = 'm_5'
        else:
            time_int = 'd_7'
        map_aprs, plot_speed, plot_alt, plot_course, rows = figs.create_map_aprs(
            type_aprs, prop_aprs, time_int)
        return render_template('aprs.html', type_aprs=type_aprs, times=times, map_aprs=map_aprs, plot_speed=plot_speed, plot_alt=plot_alt, plot_course=plot_course, rows=rows)


@cache.cached(timeout=60)
@t.include
@app.route('/aircraft')
def aircraft():
    g.track_var['page'] = 'aircraft'
    return render_template('aircraft.html')


@cache.cached(timeout=60)
@t.include
@app.route('/paragliding')
def paragliding():
    g.track_var['page'] = 'paragliding'
    return render_template('paragliding.html')


@cache.cached(timeout=60)
@t.include
@app.route('/soaring')
def soaring():
    g.track_var['page'] = 'soaring'
    return render_template('soaring.html')


@cache.cached(timeout=60)
@t.include
@app.route('/n5777v')
def n5777v():
    g.track_var['page'] = 'n5777v'
    return render_template('n5777v.html')


@cache.cached(timeout=60)
@t.include
@app.route('/galleries')
def galleries():
    g.track_var['page'] = 'galleries'
    rows = flickr.get_gal_rows(5)
    return render_template('galleries.html', rows=rows, title='Galleries')


@cache.cached(timeout=60)
@t.include
@app.route('/galleries/<id>')
def gallery(id):
    g.track_var['page'] = 'gallery'
    g.track_var['gallery'] = str(id)
    rows, gals = flickr.get_photo_rows(id, 5)
    return render_template('galleries.html', rows=rows, title=gals[id]['title'])


@cache.cached(timeout=60)
@t.include
@app.route('/galleries/<id>/<ph>')
def image(id, ph):
    g.track_var['page'] = 'photo'
    g.track_var['gallery'] = str(id)
    g.track_var['photo'] = str(ph)
    gals = flickr.load_gals()
    image = {
        'thumb': gals[id]['photos'][ph]['thumb'],
        'large': gals[id]['photos'][ph]['large'],
    }
    return render_template('image.html', image=image, title='photo')


@cache.cached(timeout=60)
@t.include
@app.route('/travel')
def travel():
    g.track_var['page'] = 'travel'
    return render_template('travel.html')


@cache.cached(timeout=60)
@t.include
@app.route('/scuba')
def scuba():
    g.track_var['page'] = 'scuba'
    return render_template('scuba.html')


@cache.cached(timeout=60)
@t.include
@app.route('/fishing')
def fishing():
    g.track_var['page'] = 'fishing'
    return render_template('fishing.html')


@cache.cached(timeout=60)
@t.include
@app.route('/oilgas/summary')
def oilgas_summary():
    g.track_var['page'] = 'oilgas/summary'
    df = pd.read_feather('static/oilgas_sum.feather')
    df = df.dropna(axis=0)
    df.sort_values(by='oil_cum', inplace=True, ascending=False)
    df = df[:10000]
    rows = []
    for _, row in df.iterrows():
        r = {}
        r['field'] = row['field']
        r['lease'] = row['lease']
        r['well'] = row['well']
        r['operator'] = row['operator']
        r['api'] = row['api']
        r['oil_cum'] = row['oil_cum']
        r['water_cum'] = row['water_cum']
        r['gas_cum'] = row['gas_cum']
        r['wtrstm_cum'] = row['wtrstm_cum']
        rows.append(r)
    return render_template('oilgas_summary.html', rows=rows)


@cache.cached(timeout=60)
@t.include
@app.route('/oilgas/details/<api>')
def oilgas_detail(api):
    g.track_var['page'] = 'oilgas/details'
    g.track_var['api'] = str(api)
    graph_oilgas, header = figs.get_graph_oilgas(str(api))
    graph_cyclic_jobs = figs.get_cyclic_jobs(header)
    graph_offset_oil, graph_offset_stm, graph_offset_wtr, graph_offset_oil_ci, graph_offset_stm_ci, graph_offset_wtr_ci, map_offsets, offsets = figs.get_offsets_oilgas(
        header, 0.1)
    return render_template('oilgas_details.html', header=header, plot=graph_oilgas, plot_offset_oil=graph_offset_oil, plot_offset_stm=graph_offset_stm, plot_offset_wtr=graph_offset_wtr, plot_offset_oil_ci=graph_offset_oil_ci, plot_offset_stm_ci=graph_offset_stm_ci, plot_offset_wtr_ci=graph_offset_wtr_ci, plot_cyclic_jobs=graph_cyclic_jobs, offsets=offsets)

@cache.cached(timeout=60)
@t.include
@app.route('/oilgas/map')
def oilgas_map():
    g.track_var['page'] = 'oilgas/map'
    return render_template('oilgas_map.html')


@cache.cached(timeout=60)
@t.include
@app.route('/about')
def about():
    g.track_var['page'] = 'about'
    return render_template('about.html')


@app.route('/login')
def login_template():
    return render_template('login.html')


@app.route('/auth/login', methods=['POST'])
def login_user():
    email = request.form['email']
    password = request.form['password']
    if User.login_valid(email, password):
        User.login(email)
        user = User.get_by_email(email)
        return render_template('profile.html', blogs=user.get_blogs(), email=session['email'])
    else:
        session['email'] = None
        return False


@app.route('/blogs/<string:user_id>')
@app.route('/blogs')
def user_blogs(user_id=None):
    if user_id is not None:
        user = User.get_by_id(user_id)
    else:
        user = User.get_by_email(session['email'])
    blogs = user.get_blogs()
    return render_template("user_blogs.html", blogs=blogs, email=user.email)


@app.route('/posts/<string:blog_id>')
@app.route('/posts')
def blog_posts(blog_id='bca7359faed442669aa888a2657b331f'):
    blog = Blog.from_mongo(blog_id)
    posts = blog.get_posts()
    return render_template('posts.html', posts=posts, blog_title=blog.title, blog_id=blog._id)


@app.route('/blogs/new', methods=['POST', 'GET'])
def create_new_blog():
    if request.method == 'GET':
        return render_template('new_blog.html')
    else:
        title = request.form['title']
        description = request.form['description']
        user = User.get_by_email(session['email'])
        new_blog = Blog(user.email, title, description, user._id)
        new_blog.save_to_mongo()
        return make_response(user_blogs(user._id))


@app.route('/posts/new/<string:blog_id>', methods=['POST', 'GET'])
def create_new_post(blog_id):
    if request.method == 'GET':
        return render_template('new_post.html', blog_id=blog_id)
    else:
        title = request.form['title']
        content = request.form['content']
        user = User.get_by_email(session['email'])
        new_post = Post(blog_id, title, content, user.email)
        new_post.save_to_mongo()
        return make_response(blog_posts(blog_id))


@app.route('/weather/aviation/map', methods=['GET', 'POST'])
def map_awc_update():
    prop_awc = request.args['prop_awc']
    lat = request.args['lat']
    lon = request.args['lon']
    zoom = request.args['zoom']
    satellite = request.args['satellite']
    radar = request.args['radar']
    analysis = request.args['analysis']
    lightning = request.args['lightning']
    precip = request.args['precip']
    watchwarn = request.args['watchwarn']
    temp = request.args['temp']
    graphJSON = figs.create_map_awc(
        prop_awc, lat, lon, zoom, satellite, radar, lightning, analysis, precip, watchwarn, temp)
    return graphJSON


@app.route('/aprs/map', methods=['GET', 'POST'])
def map_aprs_change():
    type_aprs = request.args['type_aprs']
    prop_aprs = request.args['prop_aprs']
    time_int = request.args['time_int']
    map_aprs, plot_speed, plot_alt, plot_course, rows = figs.create_map_aprs(
        type_aprs, prop_aprs, time_int)
    data = {}
    data['map_aprs'] = json.loads(map_aprs)
    data['plot_speed'] = json.loads(plot_speed)
    data['plot_alt'] = json.loads(plot_alt)
    data['plot_course'] = json.loads(plot_course)
    data['rows'] = rows
    return json.dumps(data, default=myconverter)


@app.route('/station/history/graphs', methods=['GET', 'POST'])
def graph_wx_change():
    time_int = request.args['time_int']
    fig_td, fig_pr, fig_cb, fig_pc, fig_wd, fig_su, fig_wr, fig_thp = figs.create_wx_figs(
        time_int, sid)
    data = {}
    data['fig_td'] = json.loads(fig_td)
    data['fig_pr'] = json.loads(fig_pr)
    data['fig_cb'] = json.loads(fig_cb)
    data['fig_pc'] = json.loads(fig_pc)
    data['fig_wd'] = json.loads(fig_wd)
    data['fig_su'] = json.loads(fig_su)
    data['fig_wr'] = json.loads(fig_wr)
    data['fig_thp'] = json.loads(fig_thp)
    return json.dumps(data, default=myconverter)


@app.route('/station/live/data', methods=['GET', 'POST'])
def get_station_live():
    wx = figs.get_wx_latest(sid)
    return json.dumps(wx, default=myconverter)


@app.route('weather/soundings/image', methods=['GET', 'POST'])
def sounding_update():
    sid = request.args['sid']
    img = figs.get_image(sid)
    return json.dumps(img.decode('unicode_escape'))


@app.route('/iot/graph', methods=['GET', 'POST'])
def graph_iot_change():
    sensor_iot = request.args.getlist("sensor_iot[]")
    time_int = request.args['time_int']
    graphJSON = figs.create_graph_iot(sensor_iot, time_int)
    return graphJSON


if __name__ == '__main__':
    app.run(threaded=True, port=5000)
