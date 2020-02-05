import os
import atexit
import json
import datetime

from areas import aprs, flickr, iot, oilgas, weather
from fastapi import FastAPI, Query, Form
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
import uvicorn
from typing import List
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse

app = FastAPI()

origins = [
    'https://www.kk6gpv.net',
    'https://api.kk6gpv.net',
    'https://idpgis.ncep.noaa.gov',
    'https://nowcoast.noaa.gov',
    'http://localhost',
    'http://localhost:3000',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.add_middleware(
    GZipMiddleware,
    minimum_size=500
)

sid = os.environ['SID']

times = dict(m_5='5m', h_1='1h', h_6='6h', d_1='1d',
             d_2='2d', d_7='7d', d_30='30d')


def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()


@app.get('/')
def main():
    return {'api': 'kk6gpv.net'}


@app.get('/aprs/latest')
async def aprs_latest():
    last = aprs.get_aprs_latest()
    data = {}
    data['last'] = last
    json_compatible_item_data = jsonable_encoder(data)
    return JSONResponse(content=json_compatible_item_data)


@app.get('/aprs/map')
async def aprs_map(type_aprs: str, prop_aprs: str, time_int: str):
    map_aprs, plot_speed, plot_alt, plot_course, rows = aprs.create_map_aprs(
        type_aprs, prop_aprs, time_int)
    data = {}
    data['map_aprs'] = json.loads(map_aprs)
    data['plot_speed'] = json.loads(plot_speed)
    data['plot_alt'] = json.loads(plot_alt)
    data['plot_course'] = json.loads(plot_course)
    data['rows'] = rows
    json_compatible_item_data = jsonable_encoder(data)
    return JSONResponse(content=json_compatible_item_data)


@app.get('/aprs/igate_range')
async def aprs_igate_range(time_int: str):
    range_aprs = aprs.create_range_aprs(time_int)
    data = {}
    data['range_aprs'] = json.loads(range_aprs)
    json_compatible_item_data = jsonable_encoder(data)
    return JSONResponse(content=json_compatible_item_data)


@app.get('/iot/graph')
async def iot_graph(time_int: str, sensor_iot: List[str] = Query(None)):
    graph = iot.create_graph_iot(sensor_iot, time_int)
    data = {}
    try:
        data['graph'] = json.loads(graph)
    except:
        pass
    json_compatible_item_data = jsonable_encoder(data)
    return JSONResponse(content=json_compatible_item_data)


@app.get('/oilgas/tags/get')
async def oilgas_tags_get(api: str):
    tags = oilgas.get_tags_oilgas(str(api))
    try:
        tags.pop('_id')
    except:
        pass
    data = {}
    try:
        data['tags'] = tags
    except:
        pass
    json_compatible_item_data = jsonable_encoder(data)
    return JSONResponse(content=json_compatible_item_data)


@app.put('/oilgas/tags/set')
async def oilgas_tags_set(api: str, tags: List[str] = Query(None)):
    oilgas.set_tags_oilgas(api, tags)


@app.get('/oilgas/header/tags')
async def oilgas_header_tags(tags: List[str] = Query(None)):
    headers = oilgas.get_header_tags_oilgas(tags)
    data = {}
    try:
        data['headers'] = headers
    except:
        pass
    json_compatible_item_data = jsonable_encoder(data)
    return JSONResponse(content=json_compatible_item_data)


@app.get('/oilgas/header/details')
async def oilgas_header_details(api: str):
    header = oilgas.get_header_oilgas(str(api))
    data = {}
    try:
        data['header'] = header
    except:
        pass
    json_compatible_item_data = jsonable_encoder(data)
    return JSONResponse(content=json_compatible_item_data)


@app.get('/oilgas/prodinj/graph')
async def oilgas_prodinj_graph(api: str, axis: str):
    graph_oilgas = oilgas.get_graph_oilgas(str(api), axis)
    data = {}
    try:
        data['graph_oilgas'] = json.loads(graph_oilgas)
    except:
        pass
    json_compatible_item_data = jsonable_encoder(data)
    return JSONResponse(content=json_compatible_item_data)


@app.put('/oilgas/decline/solve')
async def oilgas_tags_set(api: str):
    oilgas.set_decline_oilgas(api)


async def oilgas_decline_graph(api: str, axis: str):
    graph_decline, graph_decline_cum = oilgas.get_decline_oilgas(
        str(api), axis)
    data = {}
    try:
        data['graph_decline'] = json.loads(graph_decline)
        data['graph_decline_cum'] = json.loads(graph_decline_cum)
    except:
        pass
    json_compatible_item_data = jsonable_encoder(data)
    return JSONResponse(content=json_compatible_item_data)


@app.get('/oilgas/decline/graph')
async def oilgas_decline_graph(api: str, axis: str):
    graph_decline, graph_decline_cum = oilgas.get_decline_oilgas(
        str(api), axis)
    data = {}
    try:
        data['graph_decline'] = json.loads(graph_decline)
        data['graph_decline_cum'] = json.loads(graph_decline_cum)
    except:
        pass
    json_compatible_item_data = jsonable_encoder(data)
    return JSONResponse(content=json_compatible_item_data)


@app.get('/oilgas/crm/graph')
async def oilgas_crm_graph(api: str):
    graph_crm = oilgas.get_crm(str(api))
    data = {}
    try:
        data['graph_crm'] = json.loads(graph_crm)
    except:
        pass
    json_compatible_item_data = jsonable_encoder(data)
    return JSONResponse(content=json_compatible_item_data)


@app.get('/oilgas/cyclic/graph')
async def oilgas_cyclic_graph(api: str):
    graph_cyclic_jobs = oilgas.get_cyclic_jobs(str(api))
    data = {}
    try:
        data['graph_cyclic_jobs'] = json.loads(graph_cyclic_jobs)
    except:
        pass
    json_compatible_item_data = jsonable_encoder(data)
    return JSONResponse(content=json_compatible_item_data)


@app.get('/oilgas/offset/graphs')
async def oilgas_offset_graph(api: str, axis: str):
    graph_offset_oil, graph_offset_stm, graph_offset_wtr, graph_offset_oil_ci, graph_offset_stm_ci, graph_offset_wtr_ci, map_offsets, offsets = oilgas.get_offsets_oilgas(
        str(api), radius=0.1, axis=axis)
    data = {}
    try:
        data['graph_offset_oil'] = json.loads(graph_offset_oil)
    except:
        pass
    try:
        data['graph_offset_stm'] = json.loads(graph_offset_stm)
    except:
        pass
    try:
        data['graph_offset_wtr'] = json.loads(graph_offset_wtr)
    except:
        pass
    try:
        data['graph_offset_oil_ci'] = json.loads(graph_offset_oil_ci)
    except:
        pass
    try:
        data['graph_offset_stm_ci'] = json.loads(graph_offset_stm_ci)
    except:
        pass
    try:
        data['graph_offset_wtr_ci'] = json.loads(graph_offset_wtr_ci)
    except:
        pass
    json_compatible_item_data = jsonable_encoder(data)
    return JSONResponse(content=json_compatible_item_data)


@app.get('/photos/galleries')
async def photos_galleries():
    rows = flickr.get_gal_rows(5)
    data = {}
    data['rows'] = rows
    json_compatible_item_data = jsonable_encoder(data)
    return JSONResponse(content=json_compatible_item_data)


@app.get('/photos/gallery')
async def photos_gallery(id: str):
    rows, map_gal, title, count_photos, count_views = flickr.get_photo_rows(
        id, 5)
    data = {}
    data['title'] = title
    data['count_photos'] = count_photos
    data['count_views'] = count_views
    data['rows'] = rows
    data['map'] = json.loads(map_gal)
    json_compatible_item_data = jsonable_encoder(data)
    return JSONResponse(content=json_compatible_item_data)


@app.get('/photos/photo')
async def photos_photo(id: str):
    image, map_photo = flickr.get_photo(id)
    data = {}
    data['image'] = image
    try:
        data['map'] = json.loads(map_photo)
    except:
        pass
    json_compatible_item_data = jsonable_encoder(data)
    return JSONResponse(content=json_compatible_item_data)


@app.get('/station/history/graphs')
async def station_history_graphs(time_int: str):
    fig_td, fig_pr, fig_cb, fig_pc, fig_wd, fig_su, fig_wr, fig_thp = weather.create_wx_figs(
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
    json_compatible_item_data = jsonable_encoder(data)
    return JSONResponse(content=json_compatible_item_data)


@app.get('/station/live/data')
async def station_live_data():
    wx = weather.get_wx_latest(sid)
    data = {}
    data['wx'] = wx
    json_compatible_item_data = jsonable_encoder(data)
    return JSONResponse(content=json_compatible_item_data)


@app.get('/weather/aviation/map')
async def weather_aviation_map(
    prop_awc: str = 'flight_category',
    lat: float = 29.78088,
    lon: float = -95.42041,
    zoom: int = 6,
    stations: str = '1',
    infrared: str = '0',
    radar: str = '1',
    analysis: str = '1',
    lightning: str = '1',
    precip: str = '0',
    watchwarn: str = '0',
    temp: str = '0',
    visible: str = '0'
):
    graphJSON = weather.create_map_awc(
        prop_awc, lat, lon, zoom, stations, infrared, radar, lightning, analysis, precip, watchwarn, temp, visible)
    data = {}
    data['map'] = json.loads(graphJSON)
    json_compatible_item_data = jsonable_encoder(data)
    return JSONResponse(content=json_compatible_item_data)


@app.get('/weather/soundings/image')
async def weather_soundings_images(sid: str):
    img = weather.get_image(sid)
    json_compatible_item_data = jsonable_encoder(img.decode('unicode_escape'))
    return JSONResponse(content=json_compatible_item_data)
