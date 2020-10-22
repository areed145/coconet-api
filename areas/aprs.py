import os
import numpy as np
import pandas as pd
from pymongo import MongoClient
import plotly
import plotly.graph_objs as go
import json
from datetime import datetime, timezone
from matplotlib.colors import (
    LinearSegmentedColormap,
    rgb2hex,
)
from utils import config, helpers


def create_range_aprs(time):
    client = MongoClient(os.environ["MONGODB_CLIENT"])
    lat = 29.780880
    lon = -95.420410

    start, now = helpers.get_time_range(time)
    db = client.aprs
    df = pd.DataFrame(
        list(
            db.raw.find(
                {
                    "script": "entry",
                    "latitude": {"$exists": True, "$ne": None},
                    "timestamp_": {"$gt": start, "$lte": now},
                }
            ).sort([("timestamp_", -1)])
        )
    )
    df["dist"] = helpers.haversine_np(
        lon, lat, df["longitude"], df["latitude"]
    )
    df["month"] = df["timestamp_"].apply(
        lambda row: str(row.year) + "-" + str(row.month).zfill(2)
    )
    df["dist_"] = np.round(df["dist"] * 1) / 1
    df = df[df["dist"] <= 250]

    c5 = np.array([245 / 256, 200 / 256, 66 / 256, 1])
    c4 = np.array([245 / 256, 218 / 256, 66 / 256, 1])
    c3 = np.array([188 / 256, 245 / 256, 66 / 256, 1])
    c2 = np.array([108 / 256, 201 / 256, 46 / 256, 1])
    c1 = np.array([82 / 256, 138 / 256, 45 / 256, 1])
    c0 = np.array([24 / 256, 110 / 256, 45 / 256, 1])
    total = len(df["month"].unique())
    cm = LinearSegmentedColormap.from_list(
        "custom", [c0, c1, c2, c3, c4, c5], N=total
    )

    data = []
    for idx, month in enumerate(df["month"].unique()):
        color = rgb2hex(cm(idx / total))
        df2 = df[df["month"] == month]
        df2 = df2.groupby(by="dist_").count()
        data.append(
            go.Scatter(
                x=df2.index,
                y=df2["_id"],
                name=month,
                line=dict(color=color, width=3, shape="spline", smoothing=0.3),
                mode="lines",
            ),
        )

    layout = go.Layout(
        autosize=True,
        hoverlabel=dict(font=dict(family="Ubuntu")),
        yaxis=dict(
            domain=[0.02, 0.98],
            type="log",
            title="Frequency",
            fixedrange=False,
        ),
        xaxis=dict(type="log", title="Distance (mi)", fixedrange=False,),
        margin=dict(r=50, t=30, b=30, l=60, pad=0),
        #     showlegend=False,
    )

    graphJSON = json.dumps(
        dict(data=data, layout=layout), cls=plotly.utils.PlotlyJSONEncoder
    )
    client.close()
    return graphJSON


def create_map_aprs(script, prop, time):
    params = {
        "none": [0, 0, 0, 0, ""],
        "altitude": [0, 1000, 3.2808, 0, "ft"],
        "speed": [0, 100, 0.621371, 0, "mph"],
        "course": [0, 359, 1, 0, "degrees"],
    }
    client = MongoClient(os.environ["MONGODB_CLIENT"])
    db = client.aprs
    start, now = helpers.get_time_range(time)
    if script == "prefix":
        df = pd.DataFrame(
            list(
                db.raw.find(
                    {
                        "script": script,
                        "from": "KK6GPV",
                        "latitude": {"$exists": True, "$ne": None},
                        "timestamp_": {"$gt": start, "$lte": now},
                    }
                ).sort([("timestamp_", -1)])
            )
        )
    else:
        df = pd.DataFrame(
            list(
                db.raw.find(
                    {
                        "script": script,
                        "latitude": {"$exists": True, "$ne": None},
                        "timestamp_": {"$gt": start, "$lte": now},
                    }
                ).sort([("timestamp_", -1)])
            )
        )

    if prop == "none":
        data_map = [
            go.Scattermapbox(
                lat=df["latitude"],
                lon=df["longitude"],
                text=df["raw"],
                mode="markers",
                marker=dict(size=10),
            )
        ]
    else:
        cs = config.cs_normal
        if prop == "course":
            cmin = 0
            cmax = 359
            cs = config.cs_circle
        else:
            cmin = df[prop].quantile(0.01)
            cmax = df[prop].quantile(0.99)
        data_map = [
            go.Scattermapbox(
                lat=df["latitude"],
                lon=df["longitude"],
                text=df["raw"],
                mode="markers",
                marker=dict(
                    size=10,
                    color=params[prop][2] * df[prop] + params[prop][3],
                    colorbar=dict(title=params[prop][4]),
                    colorscale=cs,
                    cmin=params[prop][2] * cmin + params[prop][3],
                    cmax=params[prop][2] * cmax + params[prop][3],
                ),
            )
        ]
    layout_map = go.Layout(
        autosize=True,
        font=dict(family="Ubuntu"),
        showlegend=False,
        hovermode="closest",
        hoverlabel=dict(font=dict(family="Ubuntu")),
        uirevision=True,
        margin=dict(r=0, t=0, b=0, l=0, pad=0),
        mapbox=dict(
            bearing=0,
            center=dict(lat=30, lon=-95),
            accesstoken=os.environ["MAPBOX_TOKEN"],
            style="mapbox://styles/areed145/ck3j3ab8d0bx31dsp37rshufu",
            pitch=0,
            zoom=6,
        ),
    )

    data_speed = [
        go.Scatter(
            x=df["timestamp_"],
            y=params["speed"][2] * df["speed"] + params["speed"][3],
            name="Speed (mph)",
            line=dict(color="#96F42E", width=3, shape="spline", smoothing=0.3),
            mode="lines",
        ),
    ]

    layout_speed = go.Layout(
        autosize=True,
        height=200,
        hoverlabel=dict(font=dict(family="Ubuntu")),
        yaxis=dict(
            domain=[0.02, 0.98],
            title="Speed (mph)",
            fixedrange=True,
            titlefont=dict(color="#96F42E"),
        ),
        xaxis=dict(type="date", fixedrange=False, range=[start, now]),
        margin=dict(r=50, t=30, b=30, l=60, pad=0),
        showlegend=False,
    )

    data_alt = [
        go.Scatter(
            x=df["timestamp_"],
            y=params["altitude"][2] * df["altitude"] + params["altitude"][3],
            name="Altitude (ft)",
            line=dict(color="#2ED9F4", width=3, shape="spline", smoothing=0.3),
            mode="lines",
        ),
    ]

    layout_alt = go.Layout(
        autosize=True,
        font=dict(family="Ubuntu"),
        hoverlabel=dict(font=dict(family="Ubuntu")),
        height=200,
        yaxis=dict(
            domain=[0.02, 0.98],
            title="Altitude (ft)",
            fixedrange=True,
            titlefont=dict(color="#2ED9F4"),
        ),
        xaxis=dict(type="date", fixedrange=False, range=[start, now]),
        margin=dict(r=50, t=30, b=30, l=60, pad=0),
        showlegend=False,
    )

    data_course = [
        go.Scatter(
            x=df["timestamp_"],
            y=params["course"][2] * df["course"] + params["course"][3],
            name="Course (degrees)",
            line=dict(color="#B02EF4", width=3, shape="spline", smoothing=0.3),
            mode="lines",
        ),
    ]

    layout_course = go.Layout(
        autosize=True,
        font=dict(family="Ubuntu"),
        hoverlabel=dict(font=dict(family="Ubuntu")),
        height=200,
        yaxis=dict(
            domain=[0.02, 0.98],
            title="Course (degrees)",
            fixedrange=True,
            titlefont=dict(color="#B02EF4"),
        ),
        xaxis=dict(type="date", fixedrange=False, range=[start, now]),
        margin=dict(r=50, t=30, b=30, l=60, pad=0),
        showlegend=False,
    )

    graphJSON_map = json.dumps(
        dict(data=data_map, layout=layout_map),
        cls=plotly.utils.PlotlyJSONEncoder,
    )

    graphJSON_speed = json.dumps(
        dict(data=data_speed, layout=layout_speed),
        cls=plotly.utils.PlotlyJSONEncoder,
    )

    graphJSON_alt = json.dumps(
        dict(data=data_alt, layout=layout_alt),
        cls=plotly.utils.PlotlyJSONEncoder,
    )

    graphJSON_course = json.dumps(
        dict(data=data_course, layout=layout_course),
        cls=plotly.utils.PlotlyJSONEncoder,
    )

    df["timestamp_"] = df["timestamp_"].apply(
        lambda x: x.strftime("%Y-%m-%d %H:%M:%S")
    )
    df["latitude"] = np.round(df["latitude"], 3)
    df["longitude"] = np.round(df["longitude"], 3)
    df["speed"] = np.round(df["speed"], 2)
    df["altitude"] = np.round(df["altitude"], 1)
    df["course"] = np.round(df["course"], 1)
    df = df.fillna("")
    rows = []
    for _, row in df.iterrows():
        r = {}
        r["timestamp_"] = row["timestamp_"]
        r["from"] = row["from"]
        r["to"] = row["to"]
        r["via"] = row["via"]
        # r['latitude'] = row['latitude']
        # r['longitude'] = row['longitude']
        r["speed"] = row["speed"]
        r["altitude"] = row["altitude"]
        r["course"] = row["course"]
        r["comment"] = row["comment"]
        rows.append(r)
    client.close()
    return (
        graphJSON_map,
        graphJSON_speed,
        graphJSON_alt,
        graphJSON_course,
        rows,
    )


def get_aprs_latest():
    client = MongoClient(os.environ["MONGODB_CLIENT"])
    db = client.aprs
    df = pd.DataFrame(
        list(
            db.raw.find(
                {
                    "script": "prefix",
                    "from": "KK6GPV",
                    "latitude": {"$exists": True, "$ne": None},
                }
            )
            .sort([("timestamp_", -1)])
            .limit(1)
        )
    )
    last = {}
    last["timestamp_"] = (
        df["timestamp_"]
        .apply(lambda x: x.strftime("%Y-%m-%d %H:%M:%S"))
        .values[0]
    )
    time_ago = int(
        (
            datetime.now(timezone.utc)
            - pd.to_datetime(df["timestamp_"].values[0])
        )
        / np.timedelta64(1, "s")
    )
    last["hour"], last["min"], last["sec"] = helpers.convert(time_ago)
    last["latitude"] = df["latitude"].values[0]
    last["longitude"] = df["longitude"].values[0]
    return last
