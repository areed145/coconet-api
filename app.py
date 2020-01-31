# import base64
import os
# import time
import atexit
import orjson
import datetime

from helpers import figs, flickr
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
    last = figs.get_aprs_latest()
    data = {}
    data['last'] = last
    json_compatible_item_data = jsonable_encoder(data)
    return JSONResponse(content=json_compatible_item_data)


@app.get('/aprs/map')
async def aprs_map(type_aprs: str, prop_aprs: str, time_int: str):
    map_aprs, plot_speed, plot_alt, plot_course, rows = figs.create_map_aprs(
        type_aprs, prop_aprs, time_int)
    data = {}
    data['map_aprs'] = orjson.loads(map_aprs)
    data['plot_speed'] = orjson.loads(plot_speed)
    data['plot_alt'] = orjson.loads(plot_alt)
    data['plot_course'] = orjson.loads(plot_course)
    data['rows'] = rows
    json_compatible_item_data = jsonable_encoder(data)
    return JSONResponse(content=json_compatible_item_data)


@app.get('/aprs/igate_range')
async def aprs_igate_range(time_int: str):
    range_aprs = figs.create_range_aprs(time_int)
    data = {}
    data['range_aprs'] = orjson.loads(range_aprs)
    json_compatible_item_data = jsonable_encoder(data)
    return JSONResponse(content=json_compatible_item_data)


@app.get('/iot/graph')
async def iot_graph(time_int: str, sensor_iot: List[str] = Query(None)):
    graph = figs.create_graph_iot(sensor_iot, time_int)
    data = {}
    try:
        data['graph'] = orjson.loads(graph)
    except:
        pass
    json_compatible_item_data = jsonable_encoder(data)
    return JSONResponse(content=json_compatible_item_data)


@app.get('/oilgas/tags/get')
async def oilgas_tags_get(api: str):
    tags = figs.get_tags_oilgas(str(api))
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
    figs.set_tags_oilgas(api, tags)


@app.get('/oilgas/header/tags')
async def oilgas_header_tags(tags: List[str] = Query(None)):
    headers = figs.get_header_tags_oilgas(tags)
    data = {}
    try:
        data['headers'] = headers
    except:
        pass
    json_compatible_item_data = jsonable_encoder(data)
    return JSONResponse(content=json_compatible_item_data)


@app.get('/oilgas/header/details')
async def oilgas_header_details(api: str):
    header = figs.get_header_oilgas(str(api))
    data = {}
    try:
        data['header'] = header
    except:
        pass
    json_compatible_item_data = jsonable_encoder(data)
    return JSONResponse(content=json_compatible_item_data)


@app.get('/oilgas/prodinj/graph')
async def oilgas_prodinj_graph(api: str, axis: str):
    graph_oilgas = figs.get_graph_oilgas(str(api), axis)
    data = {}
    data['graph_oilgas'] = orjson.loads(graph_oilgas)
    try:
        data['graph_oilgas'] = orjson.loads(graph_oilgas)
    except:
        pass
    json_compatible_item_data = jsonable_encoder(data)
    return JSONResponse(content=json_compatible_item_data)


@app.get('/oilgas/decline/graph')
async def oilgas_decline_graph(api: str, axis: str):
    graph_decline = figs.get_decline_oilgas(str(api), axis)
    data = {}
    try:
        data['graph_decline'] = orjson.loads(graph_decline)
    except:
        pass
    json_compatible_item_data = jsonable_encoder(data)
    return JSONResponse(content=json_compatible_item_data)


@app.get('/oilgas/crm/graph')
async def oilgas_crm_graph(api: str):
    graph_crm = figs.get_crm(str(api))
    data = {}
    try:
        data['graph_crm'] = orjson.loads(graph_crm)
    except:
        pass
    json_compatible_item_data = jsonable_encoder(data)
    return JSONResponse(content=json_compatible_item_data)


@app.get('/oilgas/cyclic/graph')
async def oilgas_cyclic_graph(api: str):
    graph_cyclic_jobs = figs.get_cyclic_jobs(str(api))
    data = {}
    try:
        data['graph_cyclic_jobs'] = orjson.loads(graph_cyclic_jobs)
    except:
        pass
    json_compatible_item_data = jsonable_encoder(data)
    return JSONResponse(content=json_compatible_item_data)


@app.get('/oilgas/offset/graphs')
async def oilgas_offset_graph(api: str, axis: str):
    graph_offset_oil, graph_offset_stm, graph_offset_wtr, graph_offset_oil_ci, graph_offset_stm_ci, graph_offset_wtr_ci, map_offsets, offsets = figs.get_offsets_oilgas(
        str(api), radius=0.1, axis=axis)
    data = {}
    try:
        data['graph_offset_oil'] = orjson.loads(graph_offset_oil)
    except:
        pass
    try:
        data['graph_offset_stm'] = orjson.loads(graph_offset_stm)
    except:
        pass
    try:
        data['graph_offset_wtr'] = orjson.loads(graph_offset_wtr)
    except:
        pass
    try:
        data['graph_offset_oil_ci'] = orjson.loads(graph_offset_oil_ci)
    except:
        pass
    try:
        data['graph_offset_stm_ci'] = orjson.loads(graph_offset_stm_ci)
    except:
        pass
    try:
        data['graph_offset_wtr_ci'] = orjson.loads(graph_offset_wtr_ci)
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
    data['map'] = orjson.loads(map_gal)
    json_compatible_item_data = jsonable_encoder(data)
    return JSONResponse(content=json_compatible_item_data)


@app.get('/photos/photo')
async def photos_photo(id: str):
    image, map_photo = flickr.get_photo(id)
    data = {}
    data['image'] = image
    try:
        data['map'] = orjson.loads(map_photo)
    except:
        pass
    json_compatible_item_data = jsonable_encoder(data)
    return JSONResponse(content=json_compatible_item_data)


@app.get('/station/history/graphs')
async def station_history_graphs(time_int: str):
    fig_td, fig_pr, fig_cb, fig_pc, fig_wd, fig_su, fig_wr, fig_thp = figs.create_wx_figs(
        time_int, sid)
    data = {}
    data['fig_td'] = orjson.loads(fig_td)
    data['fig_pr'] = orjson.loads(fig_pr)
    data['fig_cb'] = orjson.loads(fig_cb)
    data['fig_pc'] = orjson.loads(fig_pc)
    data['fig_wd'] = orjson.loads(fig_wd)
    data['fig_su'] = orjson.loads(fig_su)
    data['fig_wr'] = orjson.loads(fig_wr)
    data['fig_thp'] = orjson.loads(fig_thp)
    json_compatible_item_data = jsonable_encoder(data)
    return JSONResponse(content=json_compatible_item_data)


@app.get('/station/live/data')
async def station_live_data():
    wx = figs.get_wx_latest(sid)
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
    graphJSON = figs.create_map_awc(
        prop_awc, lat, lon, zoom, stations, infrared, radar, lightning, analysis, precip, watchwarn, temp, visible)
    data = {}
    data['map'] = orjson.loads(graphJSON)
    json_compatible_item_data = jsonable_encoder(data)
    return JSONResponse(content=json_compatible_item_data)


@app.get('/weather/soundings/image')
async def weather_soundings_images(sid: str):
    img = figs.get_image(sid)
    json_compatible_item_data = jsonable_encoder(img.decode('unicode_escape'))
    return JSONResponse(content=json_compatible_item_data)
