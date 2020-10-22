import numpy as np
import pandas as pd
import plotly
import plotly.graph_objs as go
import json
from datetime import datetime, timedelta, timezone


def get_time_range(time):
    unit = time[0]
    val = int(time[2:])
    now = datetime.now(timezone.utc)
    if unit == "m":
        start = now - timedelta(minutes=val)
    if unit == "h":
        start = now - timedelta(hours=val)
    if unit == "d":
        start = now - timedelta(days=val)
    if unit == "o":
        start = now - timedelta(months=val)
    return start, now


def create_3d_plot(
    df, x, y, z, cs, x_name, y_name, z_name, x_color, y_color, z_color
):
    df = df[
        (df[x] > -9999)
        & (df[x] < 9999)
        & (df[y] > -9999)
        & (df[y] < 9999)
        & (df[z] > -9999)
        & (df[z] < 9999)
    ]

    df[x + "_u"] = np.round(df[x], 1)
    df[y + "_u"] = np.round(df[y], 1)
    df[z + "_u"] = np.round(df[z], 1)

    df = pd.pivot_table(
        df,
        values=z + "_u",
        index=[x + "_u"],
        columns=[y + "_u"],
        aggfunc=np.mean,
    )

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
        hoverlabel=dict(font=dict(family="Ubuntu")),
        scene={
            "aspectmode": "cube",
            "xaxis": {
                "title": x_name,
                "tickfont": {"family": "Ubuntu", "size": 10},
                "titlefont": {"family": "Ubuntu", "color": x_color},
                "type": "linear",
            },
            "yaxis": {
                "title": y_name,
                "tickfont": {"family": "Ubuntu", "size": 10},
                "titlefont": {"family": "Ubuntu", "color": y_color},
                "tickangle": 1,
            },
            "zaxis": {
                "title": z_name,
                "tickfont": {"family": "Ubuntu", "size": 10},
                "titlefont": {"family": "Ubuntu", "color": z_color},
            },
        },
    )
    graphJSON = json.dumps(
        dict(data=data, layout=layout), cls=plotly.utils.PlotlyJSONEncoder
    )
    return graphJSON


def haversine_np(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)

    All args must be of equal length.

    """
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = (
        np.sin(dlat / 2.0) ** 2
        + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0) ** 2
    )

    c = 2 * np.arcsin(np.sqrt(a))
    km = 6367 * c
    mi = km * 0.621371
    return mi


def convert(seconds):
    min, sec = divmod(seconds, 60)
    hour, min = divmod(min, 60)
    return hour, min, sec
