import os
import numpy as np
import pandas as pd
from pymongo import MongoClient
import gridfs
import plotly
import plotly.graph_objs as go
import json
from datetime import datetime, timezone
import base64
import re
from utils import config, helpers


def create_map_awc(
    prop: str,
    lat: float = 38,
    lon: float = -96,
    zoom: int = 3,
    stations: str = "1",
    infrared: str = "0",
    radar: str = "0",
    lightning: str = "0",
    analysis: str = "0",
    precip: str = "0",
    watchwarn: str = "0",
    temp: str = "0",
    visible: str = "0",
):
    params = {
        "flight_category": [0, 0, 0, 0, ""],
        "temp_c": [0, 100, 1.8, 32, "F"],
        "temp_c_var": [0, 100, 1.8, 0, "F"],
        "temp_c_delta": [0, 100, 1.8, 0, "F"],
        "dewpoint_c": [0, 100, 1.8, 32, "F"],
        "dewpoint_c_delta": [0, 100, 1.8, 0, "F"],
        "temp_dewpoint_spread": [0, 100, 1.8, 0, "F"],
        "altim_in_hg": [0, 100, 1, 0, "inHg"],
        "altim_in_hg_var": [0, 100, 1, 0, "inHg"],
        "altim_in_hg_delta": [0, 100, 1, 0, "inHg"],
        "wind_dir_degrees": [0, 359, 1, 0, "degrees"],
        "wind_speed_kt": [0, 100, 1, 0, "kts"],
        "wind_speed_kt_delta": [0, 100, 1, 0, "kts"],
        "wind_gust_kt": [0, 100, 1, 0, "kts"],
        "wind_gust_kt_delta": [0, 100, 1, 0, "kts"],
        "visibility_statute_mi": [0, 100, 1, 0, "mi"],
        "cloud_base_ft_agl_0": [0, 10000, 1, 0, "ft"],
        "cloud_base_ft_agl_0_delta": [0, 10000, 1, 0, "ft"],
        "sky_cover_0": [0, 100, 1, 0, "degrees"],
        "precip_in": [0, 10, 1, 0, "degrees"],
        "elevation_m": [0, 10000, 3.2808, 0, "ft"],
        "age": [0, 10000, 1, 0, "minutes"],
        "three_hr_pressure_tendency_mb": [0, 10000, 1, 0, "?"],
    }

    legend = False

    if stations == "1":
        client = MongoClient(os.environ["MONGODB_CLIENT"])
        db = client.wx
        df = pd.DataFrame(list(db.awc.find()))
        client.close()

        if prop == "temp_dewpoint_spread":
            df["temp_dewpoint_spread"] = df["temp_c"] - df["dewpoint_c"]

        if prop == "age":
            df["age"] = (
                datetime.now(timezone.utc) - df["observation_time"]
            ).astype("timedelta64[m]")

        df.dropna(subset=[prop], inplace=True)

        if prop == "flight_category":
            df_vfr = df[df["flight_category"] == "VFR"]
            df_mvfr = df[df["flight_category"] == "MVFR"]
            df_ifr = df[df["flight_category"] == "IFR"]
            df_lifr = df[df["flight_category"] == "LIFR"]
            legend = False

            data = [
                go.Scattermapbox(
                    lat=df_vfr["latitude"],
                    lon=df_vfr["longitude"],
                    text=df_vfr["raw_text"],
                    mode="markers",
                    name="VFR",
                    marker=dict(size=10, color="rgb(0,255,0)",),
                ),
                go.Scattermapbox(
                    lat=df_mvfr["latitude"],
                    lon=df_mvfr["longitude"],
                    text=df_mvfr["raw_text"],
                    mode="markers",
                    name="MVFR",
                    marker=dict(size=10, color="rgb(0,0,255)",),
                ),
                go.Scattermapbox(
                    lat=df_ifr["latitude"],
                    lon=df_ifr["longitude"],
                    text=df_ifr["raw_text"],
                    mode="markers",
                    name="IFR",
                    marker=dict(size=10, color="rgb(255,0,0)",),
                ),
                go.Scattermapbox(
                    lat=df_lifr["latitude"],
                    lon=df_lifr["longitude"],
                    text=df_lifr["raw_text"],
                    mode="markers",
                    name="LIFR",
                    marker=dict(size=10, color="rgb(255,127.5,255)",),
                ),
            ]
        elif prop == "sky_cover_0":
            df_clr = df[df["sky_cover_0"] == "CLR"]
            df_few = df[df["sky_cover_0"] == "FEW"]
            df_sct = df[df["sky_cover_0"] == "SCT"]
            df_bkn = df[df["sky_cover_0"] == "BKN"]
            df_ovc = df[df["sky_cover_0"] == "OVC"]
            df_ovx = df[df["sky_cover_0"] == "OVX"]
            legend = True

            data = [
                go.Scattermapbox(
                    lat=df_clr["latitude"],
                    lon=df_clr["longitude"],
                    text=df_clr["raw_text"],
                    mode="markers",
                    name="CLR",
                    marker=dict(size=10, color="rgb(21, 230, 234)",),
                ),
                go.Scattermapbox(
                    lat=df_few["latitude"],
                    lon=df_few["longitude"],
                    text=df_few["raw_text"],
                    mode="markers",
                    name="FEW",
                    marker=dict(size=10, color="rgb(194, 234, 21)",),
                ),
                go.Scattermapbox(
                    lat=df_sct["latitude"],
                    lon=df_sct["longitude"],
                    text=df_sct["raw_text"],
                    mode="markers",
                    name="SCT",
                    marker=dict(size=10, color="rgb(234, 216, 21)",),
                ),
                go.Scattermapbox(
                    lat=df_bkn["latitude"],
                    lon=df_bkn["longitude"],
                    text=df_bkn["raw_text"],
                    mode="markers",
                    name="BKN",
                    marker=dict(size=10, color="rgb(234, 181, 21)",),
                ),
                go.Scattermapbox(
                    lat=df_ovc["latitude"],
                    lon=df_ovc["longitude"],
                    text=df_ovc["raw_text"],
                    mode="markers",
                    name="OVC",
                    marker=dict(size=10, color="rgb(234, 77, 21)",),
                ),
                go.Scattermapbox(
                    lat=df_ovx["latitude"],
                    lon=df_ovx["longitude"],
                    text=df_ovx["raw_text"],
                    mode="markers",
                    name="OVX",
                    marker=dict(size=10, color="rgb(234, 21, 21)",),
                ),
            ]
        else:
            if prop == "wind_dir_degrees":
                cs = config.cs_circle
                cmin = 0
                cmax = 359
            elif prop == "visibility_statute_mi":
                cs = config.cs_rdgn
                cmin = 0
                cmax = 10
            elif prop == "cloud_base_ft_agl_0":
                cs = config.cs_rdgn
                cmin = 0
                cmax = 2000
            elif prop == "age":
                cs = config.cs_gnrd
                cmin = 0
                cmax = 60
            elif prop == "temp_dewpoint_spread":
                cs = config.cs_rdgn
                cmin = 0
                cmax = 5
            elif prop == "temp_c_delta":
                cs = config.cs_updown
                cmin = -3
                cmax = 3
            elif prop == "dewpoint_c_delta":
                cs = config.cs_updown
                cmin = -3
                cmax = 3
            elif prop == "altim_in_hg_delta":
                cs = config.cs_updown
                cmin = -0.03
                cmax = 0.03
            elif prop == "wind_speed_kt_delta":
                cs = config.cs_updown
                cmin = -5
                cmax = 5
            elif prop == "wind_gust_kt_delta":
                cs = config.cs_updown
                cmin = -5
                cmax = 5
            elif prop == "cloud_base_ft_agl_0_delta":
                cs = config.cs_updown
                cmin = -1000
                cmax = 1000
            else:
                cs = config.cs_normal
                cmin = df[prop].quantile(0.01)
                cmax = df[prop].quantile(0.99)

            data = [
                go.Scattermapbox(
                    lat=df["latitude"],
                    lon=df["longitude"],
                    text=df["raw_text"],
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
    else:
        data = [
            go.Scattermapbox(lat=[], lon=[], mode="markers", name="stations",)
        ]

    layers = []

    if temp == "1":
        layers.append(
            dict(
                below="traces",
                sourcetype="raster",
                source=[
                    "https://idpgis.ncep.noaa.gov/arcgis/rest/services/"
                    "NWS_Forecasts_Guidance_Warnings/NDFD_temp/MapServer/"
                    "export?transparent=true&format=png32&dpi=300&layers=show:1"
                    "&bbox={bbox-epsg-3857}&bboxSR=3857&imageSR=3857&f=image"
                ],
            )
        )
    if precip == "1":
        layers.append(
            dict(
                below="traces",
                sourcetype="raster",
                source=[
                    "https://idpgis.ncep.noaa.gov/arcgis/rest/services/"
                    "NWS_Forecasts_Guidance_Warnings/wpc_precip_hazards/MapServer/"
                    "export?transparent=true&format=png32&dpi=300&layers=show:0"
                    "&bbox={bbox-epsg-3857}&bboxSR=3857&imageSR=3857&f=image"
                ],
            )
        )
    if watchwarn == "1":
        layers.append(
            dict(
                below="traces",
                sourcetype="raster",
                source=[
                    "https://idpgis.ncep.noaa.gov/arcgis/rest/services/"
                    "NWS_Forecasts_Guidance_Warnings/watch_warn_adv/MapServer/"
                    "export?transparent=true&format=png32&dpi=300&layers=show:1"
                    "&bbox={bbox-epsg-3857}&bboxSR=3857&imageSR=3857&f=image"
                ],
            )
        )
    if infrared == "1":
        layers.append(
            dict(
                below="traces",
                # opacity=0.5,
                sourcetype="raster",
                source=[
                    "https://nowcoast.noaa.gov/arcgis/rest/services/"
                    "nowcoast/sat_meteo_imagery_time/MapServer/"
                    "export?transparent=true&format=png32&dpi=300&layers=show:20,8"
                    "&bbox={bbox-epsg-3857}&bboxSR=3857&imageSR=3857&f=image"
                ],
            )
        )
    if visible == "1":
        layers.append(
            dict(
                below="traces",
                # opacity=0.5,
                sourcetype="raster",
                source=[
                    "https://nowcoast.noaa.gov/arcgis/rest/services/"
                    "nowcoast/sat_meteo_imagery_time/MapServer/"
                    "export?transparent=true&format=png32&dpi=300&layers=show:16"
                    "&bbox={bbox-epsg-3857}&bboxSR=3857&imageSR=3857&f=image"
                ],
            )
        )
    if visible == "1" or infrared == "1":
        layers.append(
            dict(
                below="traces",
                # opacity=0.5,
                sourcetype="raster",
                source=[
                    "https://services.arcgisonline.com/ArcGIS/rest/services/"
                    "Reference/World_Boundaries_and_Places/MapServer/"
                    "export?transparent=true&format=png32&dpi=300&"
                    "bbox={bbox-epsg-3857}&bboxSR=3857&imageSR=3857&f=image"
                ],
            )
        )
    if radar == "1":
        layers.append(
            dict(
                below="traces",
                sourcetype="raster",
                source=[
                    "https://nowcoast.noaa.gov/arcgis/rest/services/"
                    "nowcoast/radar_meteo_imagery_nexrad_time/MapServer/"
                    "export?transparent=true&format=png32&dpi=300&layers=show:0"
                    "&bbox={bbox-epsg-3857}&bboxSR=3857&imageSR=3857&f=image"
                ],
            )
        )
    if lightning == "1":
        layers.append(
            dict(
                below="traces",
                sourcetype="raster",
                source=[
                    "https://nowcoast.noaa.gov/arcgis/rest/services/"
                    "nowcoast/"
                    "sat_meteo_emulated_imagery_lightningstrikedensity_goes_time/"
                    "MapServer/"
                    "export?transparent=true&format=png32&dpi=300&layers=show:0"
                    "&bbox={bbox-epsg-3857}&bboxSR=3857&imageSR=3857&f=image"
                ],
            )
        )
    if analysis == "1":
        layers.append(
            dict(
                sourcetype="raster",
                source=[
                    "https://idpgis.ncep.noaa.gov/arcgis/rest/services/"
                    "NWS_Forecasts_Guidance_Warnings/natl_fcst_wx_chart/MapServer/"
                    "export?transparent=true&format=png32&dpi=300&layers=show:1,2"
                    "&bbox={bbox-epsg-3857}&bboxSR=3857&imageSR=3857&f=image"
                ],
            )
        )

    lat = float(lat)
    lon = float(lon)
    zoom = float(zoom)

    layout = go.Layout(
        autosize=True,
        font=dict(family="Roboto Mono"),
        legend=dict(orientation="h"),
        showlegend=legend,
        hovermode="closest",
        hoverlabel=dict(font=dict(family="Roboto Mono")),
        uirevision=True,
        margin=dict(r=0, t=0, b=0, l=0, pad=0),
        mapbox=dict(
            bearing=0,
            center=dict(lat=lat, lon=lon),
            accesstoken=os.environ["MAPBOX_TOKEN"],
            style="mapbox://styles/areed145/ck3j3ab8d0bx31dsp37rshufu",
            pitch=0,
            layers=layers,
            zoom=zoom,
        ),
    )

    graphJSON = json.dumps(
        dict(data=data, layout=layout), cls=plotly.utils.PlotlyJSONEncoder
    )
    return graphJSON


def get_wx_latest(sid: str):
    client = MongoClient(os.environ["MONGODB_CLIENT"])
    db = client.wx
    wx = list(
        db.raw.find({"station_id": sid}).sort([("obs_time_utc", -1)]).limit(1)
    )[0]
    client.close()
    wx.pop("_id")
    return wx


def create_wx_figs(time: str, sid: str):
    start, now = helpers.get_time_range(time)
    client = MongoClient(os.environ["MONGODB_CLIENT"])
    db = client.wx
    df_wx_raw = pd.DataFrame(
        list(
            db.raw.find(
                {
                    "station_id": sid,
                    "obs_time_utc": {"$gt": start, "$lte": now},
                }
            ).sort([("obs_time_utc", -1)])
        )
    )
    client.close()
    df_wx_raw.index = df_wx_raw["obs_time_local"]
    # df_wx_raw = df_wx_raw.tz_localize('UTC').tz_convert('US/Central')

    for col in df_wx_raw.columns:
        try:
            df_wx_raw.loc[df_wx_raw[col] < -50, col] = pd.np.nan
        except Exception:
            pass

    df_wx_raw["cloudbase"] = (
        (df_wx_raw["temp_f"] - df_wx_raw["dewpt_f"]) / 4.4
    ) * 1000 + 50
    df_wx_raw.loc[df_wx_raw["pressure_in"] < 0, "pressure_in"] = pd.np.nan

    # df_wx_raw2 = df_wx_raw.resample('5T').mean().interpolate()
    # df_wx_raw2['dat'] = df_wx_raw2.index
    # df_wx_raw2['temp_delta'] = df_wx_raw2.temp_f.diff()
    # df_wx_raw2['precip_today_delta'] = df_wx_raw2.precip_total.diff()
    # df_wx_raw2.loc[df_wx_raw2['precip_today_delta'] < 0, 'precip_today_delta'] = 0
    # df_wx_raw2['precip_cum_in'] = df_wx_raw2.precip_today_delta.cumsum()
    # df_wx_raw2['pres_delta'] = df_wx_raw2.pressure_in.diff()
    # df_wx_raw2['dat_delta'] = df_wx_raw2.dat.diff().dt.seconds / 360
    # df_wx_raw2['dTdt'] = df_wx_raw2['temp_delta'] / df_wx_raw2['dat_delta']
    # df_wx_raw2['dPdt'] = df_wx_raw2['pres_delta'] / df_wx_raw2['dat_delta']
    # df_wx_raw3 = df_wx_raw2.drop(columns=['dat'])
    # df_wx_raw3 = df_wx_raw3.rolling(20*3).mean().add_suffix('_roll')
    # df_wx_raw = df_wx_raw2.join(df_wx_raw3)

    df_wx_raw["dat"] = df_wx_raw.index
    df_wx_raw.sort_values(by="dat", inplace=True)
    df_wx_raw["temp_delta"] = df_wx_raw.temp_f.diff()
    df_wx_raw["precip_today_delta"] = df_wx_raw.precip_total.diff()
    df_wx_raw.loc[
        df_wx_raw["precip_today_delta"] < 0, "precip_today_delta"
    ] = 0
    df_wx_raw["precip_cum_in"] = df_wx_raw.precip_today_delta.cumsum()
    df_wx_raw["pres_delta"] = df_wx_raw.pressure_in.diff()
    df_wx_raw["dat_delta"] = df_wx_raw.dat.diff().dt.seconds / 360
    df_wx_raw["dTdt"] = df_wx_raw["temp_delta"] / df_wx_raw["dat_delta"]
    df_wx_raw["dPdt"] = df_wx_raw["pres_delta"] / df_wx_raw["dat_delta"]

    df_wx_raw["date"] = df_wx_raw.index.date
    df_wx_raw["hour"] = df_wx_raw.index.hour

    df_wx_raw.loc[df_wx_raw["wind_speed_mph"] == 0, "wind_cat"] = "calm"
    df_wx_raw.loc[df_wx_raw["wind_speed_mph"] > 0, "wind_cat"] = "0-1"
    df_wx_raw.loc[df_wx_raw["wind_speed_mph"] > 1, "wind_cat"] = "1-2"
    df_wx_raw.loc[df_wx_raw["wind_speed_mph"] > 2, "wind_cat"] = "2-5"
    df_wx_raw.loc[df_wx_raw["wind_speed_mph"] > 5, "wind_cat"] = "5-10"
    df_wx_raw.loc[df_wx_raw["wind_speed_mph"] > 10, "wind_cat"] = ">10"

    df_wx_raw["wind_deg_cat"] = np.floor(df_wx_raw["wind_deg"] / 15) * 15
    df_wx_raw.loc[df_wx_raw["wind_deg_cat"] == 360, "wind_deg_cat"] = 0
    df_wx_raw["wind_deg_cat"] = (
        df_wx_raw["wind_deg_cat"].fillna(0).astype(int).astype(str)
    )

    df_wx_raw.loc[df_wx_raw["wind_speed_mph"] == 0, "wind_deg"] = pd.np.nan

    wind = df_wx_raw[["wind_cat", "wind_deg_cat"]]
    wind.loc[:, "count"] = 1
    # wind['count'] = 1
    ct = len(wind)
    wind = pd.pivot_table(
        wind,
        values="count",
        index=["wind_deg_cat"],
        columns=["wind_cat"],
        aggfunc=np.sum,
    )
    ix = np.arange(0, 360, 5)
    col = ["calm", "0-1", "1-2", "2-5", "5-10", ">10"]
    wind_temp = pd.DataFrame(data=0, index=ix, columns=col)
    for i in ix:
        for j in col:
            try:
                wind_temp.loc[i, j] = wind.loc[str(i), j]
            except Exception:
                pass
    wind_temp = wind_temp.fillna(0)
    wind_temp["calm"] = wind_temp["calm"].mean()
    for col in range(len(wind_temp.columns)):
        try:
            wind_temp.iloc[:, col] = (
                wind_temp.iloc[:, col] + wind_temp.iloc[:, col - 1]
            )
        except Exception:
            pass
    wind_temp = np.round(wind_temp / ct * 100, 2)
    wind_temp["wind_cat"] = wind_temp.index

    dt_min = df_wx_raw.index.min()
    dt_max = df_wx_raw.index.max()

    td_max = (
        max(
            df_wx_raw["temp_f"].max(),
            df_wx_raw["dewpt_f"].max(),
            df_wx_raw["heat_index_f"].max(),
            df_wx_raw["windchill_f"].max(),
        )
        + 1
    )
    td_min = (
        min(
            df_wx_raw["temp_f"].min(),
            df_wx_raw["dewpt_f"].min(),
            df_wx_raw["heat_index_f"].min(),
            df_wx_raw["windchill_f"].min(),
        )
        - 1
    )

    df_wx_raw.loc[
        df_wx_raw["heat_index_f"] == df_wx_raw["temp_f"], "heat_index_f"
    ] = pd.np.nan
    df_wx_raw.loc[
        df_wx_raw["windchill_f"] == df_wx_raw["temp_f"], "windchill_f"
    ] = pd.np.nan

    data_td = [
        go.Scatter(
            x=df_wx_raw.index,
            y=df_wx_raw["temp_f"],
            name="Temperature (F)",
            line=dict(
                color="rgb(255, 95, 63)",
                width=3,
                shape="spline",
                smoothing=0.3,
            ),
            xaxis="x",
            yaxis="y",
            mode="lines",
        ),
        go.Scatter(
            x=df_wx_raw.index,
            y=df_wx_raw["heat_index_f"],
            name="Heat Index (F)",
            line=dict(color="#F42ED0", width=3, shape="spline", smoothing=0.3),
            xaxis="x",
            yaxis="y",
            mode="lines",
        ),
        go.Scatter(
            x=df_wx_raw.index,
            y=df_wx_raw["windchill_f"],
            name="Windchill (F)",
            line=dict(color="#2EE8F4", width=3, shape="spline", smoothing=0.3),
            xaxis="x",
            yaxis="y",
            mode="lines",
        ),
        go.Scatter(
            x=df_wx_raw.index,
            y=df_wx_raw["dewpt_f"],
            name="Dewpoint (F)",
            line=dict(
                color="rgb(63, 127, 255)",
                width=3,
                shape="spline",
                smoothing=0.3,
            ),
            xaxis="x",
            yaxis="y2",
            mode="lines",
        ),
    ]

    layout_td = go.Layout(
        autosize=True,
        font=dict(family="Roboto Mono"),
        hoverlabel=dict(font=dict(family="Roboto Mono")),
        height=200,
        yaxis=dict(
            domain=[0.02, 0.98],
            title="Temperature (F)",
            range=[td_min, td_max],
            fixedrange=True,
            titlefont=dict(family="Roboto Mono", color="rgb(255, 95, 63)"),
        ),
        yaxis2=dict(
            domain=[0.02, 0.98],
            title="Dewpoint (F)",
            overlaying="y",
            side="right",
            range=[td_min, td_max],
            fixedrange=True,
            titlefont=dict(family="Roboto Mono", color="rgb(63, 127, 255)"),
        ),
        xaxis=dict(
            type="date",
            # fixedrange=True,
            range=[dt_min, dt_max],
        ),
        margin=dict(r=50, t=30, b=30, l=60, pad=0),
        showlegend=False,
    )

    data_pr = [
        go.Scatter(
            x=df_wx_raw.index,
            y=df_wx_raw["pressure_in"],
            name="Pressure (inHg)",
            line=dict(
                color="rgb(255, 127, 63)",
                width=3,
                shape="spline",
                smoothing=0.3,
            ),
            xaxis="x",
            yaxis="y",
            mode="lines",
        ),
        go.Scatter(
            x=df_wx_raw.index,
            y=df_wx_raw["humidity"],
            name="Humidity (%)",
            line=dict(
                color="rgb(127, 255, 63)",
                width=3,
                shape="spline",
                smoothing=0.3,
            ),
            xaxis="x",
            yaxis="y2",
            mode="lines",
        ),
    ]

    layout_pr = go.Layout(
        autosize=True,
        height=200,
        font=dict(family="Roboto Mono"),
        hoverlabel=dict(font=dict(family="Roboto Mono")),
        yaxis=dict(
            domain=[0.02, 0.98],
            title="Pressure (inHg)",
            # range=[0,120],
            fixedrange=True,
            titlefont=dict(family="Roboto Mono", color="rgb(255, 127, 63)"),
        ),
        yaxis2=dict(
            domain=[0.02, 0.98],
            title="Humidity (%)",
            overlaying="y",
            side="right",
            # range=[0,120],
            fixedrange=True,
            titlefont=dict(family="Roboto Mono", color="rgb(127, 255, 63)"),
        ),
        xaxis=dict(
            type="date",
            # fixedrange=True,
            range=[dt_min, dt_max],
        ),
        margin=dict(r=50, t=30, b=30, l=60, pad=0),
        showlegend=False,
    )

    data_pc = [
        go.Scatter(
            x=df_wx_raw.index,
            y=df_wx_raw["precip_rate"],
            name="Precip (in/hr)",
            line=dict(
                color="rgb(31, 190, 255)",
                width=3,
                shape="spline",
                smoothing=0.3,
            ),
            xaxis="x",
            yaxis="y",
            mode="lines",
        ),
        go.Scatter(
            x=df_wx_raw.index,
            y=df_wx_raw["precip_cum_in"],
            name="Precip Cumulative (in)",
            line=dict(
                color="rgb(63, 255, 255)",
                width=3,
                shape="spline",
                smoothing=0.3,
            ),
            xaxis="x",
            yaxis="y2",
            mode="lines",
        ),
    ]

    layout_pc = go.Layout(
        autosize=True,
        height=200,
        font=dict(family="Roboto Mono"),
        hoverlabel=dict(font=dict(family="Roboto Mono")),
        yaxis=dict(
            domain=[0.02, 0.98],
            title="Precip (in/hr)",
            # range=[0,120],
            fixedrange=True,
            titlefont=dict(family="Roboto Mono", color="rgb(31, 190, 255)"),
        ),
        yaxis2=dict(
            domain=[0.02, 0.98],
            title="Precip Cumulative (in)",
            overlaying="y",
            side="right",
            # range=[0,120],
            fixedrange=True,
            titlefont=dict(family="Roboto Mono", color="rgb(63, 255, 255)"),
        ),
        xaxis=dict(
            type="date",
            # fixedrange=True,
            range=[dt_min, dt_max],
        ),
        margin=dict(r=50, t=30, b=30, l=60, pad=0),
        showlegend=False,
    )

    data_cb = [
        go.Scatter(
            x=df_wx_raw.index,
            y=df_wx_raw["cloudbase"],
            name="Minimum Cloudbase (ft)",
            line=dict(
                color="rgb(90, 66, 245)",
                width=3,
                shape="spline",
                smoothing=0.3,
            ),
            xaxis="x",
            yaxis="y",
            mode="lines",
        ),
    ]

    layout_cb = go.Layout(
        autosize=True,
        height=200,
        font=dict(family="Roboto Mono"),
        hoverlabel=dict(font=dict(family="Roboto Mono")),
        yaxis=dict(
            domain=[0.02, 0.98],
            title="Minimum Cloudbase (ft)",
            # range=[0,120],
            fixedrange=True,
            titlefont=dict(family="Roboto Mono", color="rgb(90, 66, 245)"),
        ),
        xaxis=dict(
            type="date",
            # fixedrange=True,
            range=[dt_min, dt_max],
        ),
        margin=dict(r=50, t=30, b=30, l=60, pad=0),
        showlegend=False,
    )

    data_wd = [
        go.Scatter(
            x=df_wx_raw.index,
            y=df_wx_raw["wind_deg"],
            name="Wind Direction (degrees)",
            marker=dict(color="rgb(190, 63, 255)", size=8, symbol="x"),
            xaxis="x",
            yaxis="y",
            mode="markers",
        ),
        go.Scatter(
            x=df_wx_raw.index,
            y=df_wx_raw["wind_gust_mph"] * 0.869,
            name="Wind Gust (kts)",
            line=dict(
                color="rgb(31, 190, 15)",
                width=3,
                shape="spline",
                smoothing=0.3,
            ),
            xaxis="x",
            yaxis="y2",
            mode="lines",
        ),
        go.Scatter(
            x=df_wx_raw.index,
            y=df_wx_raw["wind_speed_mph"] * 0.869,
            name="Wind Speed (kts)",
            line=dict(
                color="rgb(127, 255, 31)",
                width=3,
                shape="spline",
                smoothing=0.3,
            ),
            xaxis="x",
            yaxis="y2",
            mode="lines",
        ),
    ]

    layout_wd = go.Layout(
        autosize=True,
        height=200,
        font=dict(family="Roboto Mono"),
        hoverlabel=dict(font=dict(family="Roboto Mono")),
        yaxis=dict(
            domain=[0.02, 0.98],
            title="Wind Direction (degrees)",
            range=[0, 360],
            fixedrange=True,
            titlefont=dict(family="Roboto Mono", color="rgb(190, 63, 255)"),
        ),
        yaxis2=dict(
            domain=[0.02, 0.98],
            title="Wind Speed / Gust (kts)",
            overlaying="y",
            side="right",
            range=[0, df_wx_raw["wind_gust_mph"].max() * 0.869],
            fixedrange=True,
            titlefont=dict(family="Roboto Mono", color="rgb(127, 255, 31)"),
        ),
        xaxis=dict(
            type="date",
            # fixedrange=True,
            range=[dt_min, dt_max],
        ),
        margin=dict(r=50, t=30, b=30, l=60, pad=0),
        showlegend=False,
    )

    data_su = [
        go.Scatter(
            x=df_wx_raw.index,
            y=df_wx_raw["solar"],
            name="Solar Radiation (W/m<sup>2</sup>)",
            line=dict(
                color="rgb(255, 63, 127)",
                width=3,
                shape="spline",
                smoothing=0.3,
            ),
            xaxis="x",
            yaxis="y",
            mode="lines",
        ),
        go.Scatter(
            x=df_wx_raw.index,
            y=df_wx_raw["uv"],
            name="UV",
            line=dict(
                color="rgb(255, 190, 63)",
                width=3,
                shape="spline",
                smoothing=0.3,
            ),
            xaxis="x",
            yaxis="y2",
            mode="lines",
        ),
    ]

    layout_su = go.Layout(
        autosize=True,
        height=200,
        font=dict(family="Roboto Mono"),
        hoverlabel=dict(font=dict(family="Roboto Mono")),
        yaxis=dict(
            domain=[0.02, 0.98],
            title="Solar Radiation (W/m<sup>2</sup>)",
            # range=[0,120],
            fixedrange=True,
            titlefont=dict(family="Roboto Mono", color="rgb(255, 63, 127)"),
        ),
        yaxis2=dict(
            domain=[0.02, 0.98],
            title="UV",
            overlaying="y",
            side="right",
            # range=[0,120],
            fixedrange=True,
            titlefont=dict(family="Roboto Mono", color="rgb(255, 190, 63)"),
        ),
        xaxis=dict(
            type="date",
            # fixedrange=True,
            range=[dt_min, dt_max],
        ),
        margin=dict(r=50, t=30, b=30, l=60, pad=0),
        showlegend=False,
    )

    t1 = go.Barpolar(
        r=wind_temp[">10"],
        theta=wind_temp["wind_cat"],
        name=">10 mph",
        width=10,
        base=0,
        marker=dict(color="#ffff00", line=dict(color="#ffff00")),
    )
    t2 = go.Barpolar(
        r=wind_temp["5-10"],
        theta=wind_temp["wind_cat"],
        name="5-10 mph",
        width=10,
        base=0,
        marker=dict(color="#ffcc00", line=dict(color="#ffcc00")),
    )
    t3 = go.Barpolar(
        r=wind_temp["2-5"],
        theta=wind_temp["wind_cat"],
        name="2-5 mph",
        width=10,
        base=0,
        marker=dict(color="#bfff00", line=dict(color="#bfff00")),
    )
    t4 = go.Barpolar(
        r=wind_temp["1-2"],
        theta=wind_temp["wind_cat"],
        name="1-2 mph",
        width=10,
        base=0,
        marker=dict(color="#00cc00", line=dict(color="#00cc00")),
    )
    t5 = go.Barpolar(
        r=wind_temp["0-1"],
        theta=wind_temp["wind_cat"],
        name="0-1 mph",
        width=10,
        base=0,
        marker=dict(color="#009999", line=dict(color="#009999")),
    )
    t6 = go.Barpolar(
        r=wind_temp["calm"],
        theta=wind_temp["wind_cat"],
        name="calm",
        width=10,
        base=0,
        marker=dict(color="#3366ff", line=dict(color="#3366ff")),
    )

    data_wr = [t1, t2, t3, t4, t5, t6]

    layout_wr = go.Layout(
        font=dict(family="Roboto Mono"),
        hoverlabel=dict(font=dict(family="Roboto Mono")),
        polar=dict(
            radialaxis=dict(
                # visible = False,
                showline=False,
                showticklabels=False,
                ticks="",
                range=[0, wind_temp[">10"].max()],
            ),
            angularaxis=dict(rotation=90, direction="clockwise",),
        ),
    )

    graphJSON_td = json.dumps(
        dict(data=data_td, layout=layout_td),
        cls=plotly.utils.PlotlyJSONEncoder,
    )

    graphJSON_pr = json.dumps(
        dict(data=data_pr, layout=layout_pr),
        cls=plotly.utils.PlotlyJSONEncoder,
    )

    graphJSON_pc = json.dumps(
        dict(data=data_pc, layout=layout_pc),
        cls=plotly.utils.PlotlyJSONEncoder,
    )

    graphJSON_cb = json.dumps(
        dict(data=data_cb, layout=layout_cb),
        cls=plotly.utils.PlotlyJSONEncoder,
    )

    graphJSON_wd = json.dumps(
        dict(data=data_wd, layout=layout_wd),
        cls=plotly.utils.PlotlyJSONEncoder,
    )

    graphJSON_su = json.dumps(
        dict(data=data_su, layout=layout_su),
        cls=plotly.utils.PlotlyJSONEncoder,
    )

    graphJSON_wr = json.dumps(
        dict(data=data_wr, layout=layout_wr),
        cls=plotly.utils.PlotlyJSONEncoder,
    )

    graphJSON_thp = helpers.create_3d_plot(
        df_wx_raw,
        "temp_f",
        "dewpt_f",
        "humidity",
        config.cs_normal,
        "Temperature (F)",
        "Dewpoint (F)",
        "Humidity (%)",
        "rgb(255, 95, 63)",
        "rgb(255, 127, 63)",
        "rgb(63, 127, 255)",
    )

    freq = "2T"
    mult = 2
    try:
        df_wx_lt = pd.DataFrame(
            list(
                db.lightning.find(
                    {"timestamp": {"$gt": start, "$lte": now},}
                ).sort([("timestamp", -1)])
            )
        )
        client.close()
        # df_wx_lt = df_wx_lt[df_wx_lt["energy"] > 0]
        df_wx_lt["distance"] = 0.621 * df_wx_lt["distance"]
        df_wx_lt["distance"] = np.round(df_wx_lt["distance"] / mult, 0) * mult
        df_wx_lt = df_wx_lt.drop(columns=["_id", "type", "energy"])
        df_pivot = df_wx_lt.pivot_table(
            index="timestamp", columns="distance", aggfunc=len
        ).fillna(0)
        df_pivot = df_pivot.resample(freq).sum()
        df_pivotT = df_pivot.T
        ymax = df_pivot.columns.max()
        df_pivotT_reindexed = df_pivotT.reindex(
            index=np.linspace(0, int(ymax), int(((1 / mult) * int(ymax)) + 1))
        )
        df_pivot = df_pivotT_reindexed.T.fillna(0)
        df_pivot = df_pivot.tz_localize("UTC")
        df_pivot = df_pivot.tz_convert("US/Central")
        df_pivot = df_pivot.tz_localize(None)
        idx = pd.date_range(
            dt_min.replace(second=0, microsecond=0),
            dt_max.replace(second=0, microsecond=0),
            freq=freq,
        )
        df_fill = pd.DataFrame(index=idx, columns=df_pivot.columns).fillna(0)
        df_fill = df_fill.tz_localize(None)
        df_pivot.index.name = None
        df_pivot = df_fill.add(df_pivot, fill_value=0)
        df_pivot = df_pivot.replace(0, pd.np.nan)
    except Exception:
        idx = pd.date_range(
            dt_min.replace(second=0, microsecond=0),
            dt_max.replace(second=0, microsecond=0),
            freq=freq,
        )
        df_fill = pd.DataFrame(
            index=idx,
            columns=np.linspace(0, int(50), int(((1 / mult) * int(50)) + 1)),
        ).fillna(0)
        df_pivot = df_fill.tz_localize(None)
        df_pivot = df_pivot.replace(0, pd.np.nan)

    data_lt = [
        go.Heatmap(
            x=df_pivot.index,
            y=df_pivot.columns,
            z=df_pivot.T.values,
            colorscale=config.scl_lightning,
            zmax=np.nanquantile(df_pivot, 0.95),
            zmin=1,
            zauto=False,
            showscale=False,
            # connectgaps=True,
        )
    ]

    layout_lt = go.Layout(
        autosize=True,
        font=dict(family="Roboto Mono"),
        hoverlabel=dict(font=dict(family="Roboto Mono")),
        height=300,
        yaxis=dict(
            range=[0, 30],
            domain=[0.02, 0.98],
            title="Distance (mi)",
            ticks="",
            fixedrange=True,
            titlefont=dict(family="Roboto Mono", color="rgb(255, 210, 63)"),
        ),
        xaxis=dict(type="date", range=[dt_min, dt_max], ticks="",),
        margin=dict(r=50, t=30, b=35, l=60, pad=0),
        showlegend=False,
    )

    graphJSON_lt = json.dumps(
        dict(data=data_lt, layout=layout_lt),
        cls=plotly.utils.PlotlyJSONEncoder,
    )

    return (
        graphJSON_td,
        graphJSON_pr,
        graphJSON_cb,
        graphJSON_pc,
        graphJSON_wd,
        graphJSON_su,
        graphJSON_wr,
        graphJSON_thp,
        graphJSON_lt,
    )


def get_image(name):
    client = MongoClient(os.environ["MONGODB_CLIENT"])
    db = client.wx_gfx
    fs = gridfs.GridFS(db)
    file = fs.find_one({"filename": name})
    img = fs.get(file._id).read()
    img = base64.b64decode(img)
    client.close()
    img = img[img.find(b"<svg") :]
    img = re.sub(b'height="\d*.\d*pt"', b'height="100%"', img)
    img = re.sub(b'width="\d*.\d*pt"', b'width="100%"', img)
    return img
