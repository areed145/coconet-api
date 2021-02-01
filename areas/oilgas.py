import os
import numpy as np
import pandas as pd
from pymongo import MongoClient
import plotly
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import json
from datetime import datetime, timedelta
import math
from utils import config, helpers, dca


def get_prodinj(wells):
    client = MongoClient(os.environ["MONGODB_CLIENT"])
    db = client.petroleum
    docs = db.doggr.aggregate(
        [{"$unwind": "$prodinj"}, {"$match": {"api": {"$in": wells}}},]
    )
    df = pd.DataFrame()
    for x in docs:
        doc = dict(x)
        df_ = pd.DataFrame(doc["prodinj"])
        df_["api"] = doc["api"]
        df = df.append(df_)

    client.close()

    df.sort_values(by=["api", "date"], inplace=True)
    df.reset_index(drop=True, inplace=True)
    df.fillna(0, inplace=True)

    for col in [
        "date",
        "oil",
        "water",
        "gas",
        "oilgrav",
        "pcsg",
        "ptbg",
        "btu",
        "steam",
        "water_i",
        "cyclic",
        "gas_i",
        "air",
        "pinjsurf",
    ]:
        if col not in df:
            df[col] = 0
        if col not in ["date", "oilgrav", "pcsg", "ptbg", "btu", "pinjsurf"]:
            df[col] = df[col] / 30.45
    return df


def ci_plot(df_offsets, prop, api, c1, c2, c3):
    df_ci = df_offsets.pivot_table(index="date", columns="api", values=prop)
    df_ci = df_ci.replace(0, pd.np.nan)
    count = df_ci.count(axis=1).fillna(0)
    sums = df_ci.sum(axis=1).fillna(0)
    ci_lb = df_ci.quantile(0.25, axis=1).fillna(0)
    ci_ub = df_ci.quantile(0.75, axis=1).fillna(0)
    val = df_ci[api]

    return [
        go.Scatter(
            x=df_ci.index,
            y=ci_ub,
            name="offest_upper_75ci",
            fill=None,
            mode="lines",
            line=dict(color=c1, shape="spline", smoothing=0.3, width=3),
        ),
        go.Scatter(
            x=df_ci.index,
            y=ci_lb,
            name="offset_lower_75ci",
            fill="tonexty",
            mode="lines",
            line=dict(color=c1, shape="spline", smoothing=0.3, width=3),
        ),
        go.Scatter(
            x=df_ci.index,
            y=count,
            name="offset_count",
            mode="lines",
            line=dict(color="#8c8c8c", shape="spline", smoothing=0.3, width=3),
        ),
        go.Scatter(
            x=df_ci.index,
            y=sums,
            name="offset_sum",
            mode="lines",
            line=dict(color=c2, shape="spline", smoothing=0.3, width=3),
        ),
        go.Scatter(
            x=df_ci.index,
            y=val,
            name="current_well",
            mode="lines",
            line=dict(color=c3, shape="spline", smoothing=0.3, width=3),
        ),
    ]


# def get_offset_distributions(api, radius):
# client = MongoClient(os.environ['MONGODB_CLIENT'])
# db = client.petroleum
# docs = db.doggr.find(
#     {'api': api}, {'api': 1, 'latitude': 1, 'longitude': 1})
# for x in docs:
#     header = dict(x)
# try:
#     r = radius/100
#     lat = header['latitude']
#     lon = header['longitude']
#     df = pd.DataFrame(list(db.doggr.find({'latitude': {'$gt': lat-r, '$lt': lat+r},
#                                           'longitude': {'$gt': lon-r, '$lt': lon+r}}, {'api': 1, 'latitude': 1, 'longitude': 1})))

#     df['dist'] = helpers.haversine_np(
#         lon, lat, df['longitude'], df['latitude'])
#     df = df[df['dist'] <= radius]
#     df.sort_values(by='dist', inplace=True)
#     df = df[:25]
#     offsets = df['api'].tolist()
#     dists = df['dist'].tolist()

#     df_offsets = get_prodinj(offsets)
#     df_offsets['date'] = pd.to_datetime(df_offsets['date'])


def get_offsets_oilgas(api, radius, axis):
    client = MongoClient(os.environ["MONGODB_CLIENT"])
    db = client.petroleum
    docs = db.doggr.find(
        {"api": api}, {"api": 1, "latitude": 1, "longitude": 1}
    )
    for x in docs:
        header = dict(x)
    try:
        r = radius / 100
        lat = header["latitude"]
        lon = header["longitude"]
        df = pd.DataFrame(
            list(
                db.doggr.find(
                    {
                        "latitude": {"$gt": lat - r, "$lt": lat + r},
                        "longitude": {"$gt": lon - r, "$lt": lon + r},
                    },
                    {"api": 1, "latitude": 1, "longitude": 1},
                )
            )
        )

        df["dist"] = helpers.haversine_np(
            lon, lat, df["longitude"], df["latitude"]
        )
        df = df[df["dist"] <= radius]
        df.sort_values(by="dist", inplace=True)
        df = df[:25]
        offsets = df["api"].tolist()
        dists = df["dist"].tolist()

        df_offsets = get_prodinj(offsets)
        df_offsets["date"] = pd.to_datetime(df_offsets["date"])

        df_offsets["distapi"] = df_offsets["api"].apply(
            lambda x: str(np.round(dists[offsets.index(x)], 3)) + " mi - " + x
        )
        df_offsets.sort_values(by="distapi", inplace=True)

        data_offset_oil = [
            go.Heatmap(
                z=df_offsets["oil"] / 30.45,
                x=df_offsets["date"],
                y=df_offsets["distapi"],
                colorscale=config.scl_oil_log,
            ),
        ]

        data_offset_stm = [
            go.Heatmap(
                z=df_offsets["steam"] / 30.45,
                x=df_offsets["date"],
                y=df_offsets["distapi"],
                colorscale=config.scl_stm_log,
            ),
        ]

        data_offset_wtr = [
            go.Heatmap(
                z=df_offsets["water"] / 30.45,
                x=df_offsets["date"],
                y=df_offsets["distapi"],
                colorscale=config.scl_wtr_log,
            ),
        ]

        layout = go.Layout(
            autosize=True,
            font=dict(family="Roboto Mono"),
            hoverlabel=dict(font=dict(family="Roboto Mono")),
            margin=dict(r=10, t=10, b=30, l=150, pad=0),
            yaxis=dict(autorange="reversed"),
            showlegend=False,
        )
        if axis == "log":
            layout_ = go.Layout(
                autosize=True,
                font=dict(family="Roboto Mono"),
                hoverlabel=dict(font=dict(family="Roboto Mono")),
                showlegend=True,
                legend=dict(orientation="h"),
                yaxis=dict(type="log"),
                margin=dict(r=50, t=30, b=30, l=60, pad=0),
            )
        else:
            layout_ = go.Layout(
                autosize=True,
                font=dict(family="Roboto Mono"),
                hoverlabel=dict(font=dict(family="Roboto Mono")),
                showlegend=True,
                legend=dict(orientation="h"),
                margin=dict(r=50, t=30, b=30, l=60, pad=0),
            )

        graphJSON_offset_oil = json.dumps(
            dict(data=data_offset_oil, layout=layout),
            cls=plotly.utils.PlotlyJSONEncoder,
        )
        graphJSON_offset_stm = json.dumps(
            dict(data=data_offset_stm, layout=layout),
            cls=plotly.utils.PlotlyJSONEncoder,
        )
        graphJSON_offset_wtr = json.dumps(
            dict(data=data_offset_wtr, layout=layout),
            cls=plotly.utils.PlotlyJSONEncoder,
        )
        graphJSON_offset_oil_ci = json.dumps(
            dict(
                data=ci_plot(
                    df_offsets,
                    "oil",
                    header["api"],
                    config.scl_oil[0][1],
                    config.scl_oil[1][1],
                    config.scl_oil[2][1],
                ),
                layout=layout_,
            ),
            cls=plotly.utils.PlotlyJSONEncoder,
        )
        graphJSON_offset_wtr_ci = json.dumps(
            dict(
                data=ci_plot(
                    df_offsets,
                    "water",
                    header["api"],
                    config.scl_wtr[0][1],
                    config.scl_wtr[1][1],
                    config.scl_wtr[2][1],
                ),
                layout=layout_,
            ),
            cls=plotly.utils.PlotlyJSONEncoder,
        )
        graphJSON_offset_stm_ci = json.dumps(
            dict(
                data=ci_plot(
                    df_offsets,
                    "steam",
                    header["api"],
                    config.scl_stm[0][1],
                    config.scl_stm[1][1],
                    config.scl_stm[2][1],
                ),
                layout=layout_,
            ),
            cls=plotly.utils.PlotlyJSONEncoder,
        )

    except Exception:
        graphJSON_offset_oil = None
        graphJSON_offset_stm = None
        graphJSON_offset_wtr = None
        graphJSON_offset_oil_ci = None
        graphJSON_offset_stm_ci = None
        graphJSON_offset_wtr_ci = None
        offsets = None

    map_offsets = None
    client.close()
    return (
        graphJSON_offset_oil,
        graphJSON_offset_stm,
        graphJSON_offset_wtr,
        graphJSON_offset_oil_ci,
        graphJSON_offset_stm_ci,
        graphJSON_offset_wtr_ci,
        map_offsets,
        offsets,
    )


def get_crm(api):
    client = MongoClient(os.environ["MONGODB_CLIENT"])
    db = client.petroleum
    docs = db.doggr.find({"api": api}, {"crm": 1})
    for x in docs:
        header = dict(x)
    try:
        df = pd.DataFrame(header["crm"]["cons"])
        df["gain"] = df["gain"].apply(lambda x: "%.3f" % x)
        df["gain"] = df["gain"].astype(float)
        df["dist"] = helpers.haversine_np(
            df["x0"], df["y0"], df["x1"], df["y1"]
        )
        df["distapi"] = df.apply(
            lambda x: str(np.round(x["dist"], 3)) + " mi - " + str(x["to"]),
            axis=1,
        )
        df = df.sort_values(by="distapi", ascending=True).reset_index()
        xs = df["gain"]
        ys = df["distapi"]
        data = [
            go.Bar(
                y=ys,
                x=xs,
                name="crm_gains",
                orientation="h",
                marker=dict(
                    color=xs, colorscale=config.cs_crm, cmin=0, cmax=1,
                ),
            )
        ]
        layout = go.Layout(
            autosize=True,
            font=dict(family="Roboto Mono"),
            hoverlabel=dict(font=dict(family="Roboto Mono")),
            margin=dict(r=10, t=10, b=30, l=150, pad=0),
            xaxis=dict(
                # range=[0, 1],
                categoryorder="array",
                categoryarray=[x for _, x in sorted(zip(ys, xs))],
            ),
            yaxis=dict(autorange="reversed"),
            showlegend=False,
        )
        graphJSON_crm = json.dumps(
            dict(data=data, layout=layout), cls=plotly.utils.PlotlyJSONEncoder
        )
    except Exception:
        graphJSON_crm = None
    client.close()
    return graphJSON_crm


def get_cyclic_jobs(api):
    client = MongoClient(os.environ["MONGODB_CLIENT"])
    db = client.petroleum
    docs = db.doggr.find({"api": api}, {"cyclic_jobs": 1})
    for x in docs:
        header = dict(x)
    try:
        df_cyclic = pd.DataFrame(header["cyclic_jobs"])
        fig_cyclic_jobs = make_subplots(rows=2, cols=1)
        total = len(df_cyclic)
        c0 = np.array([245 / 256, 200 / 256, 66 / 256, 1])
        c1 = np.array([245 / 256, 218 / 256, 66 / 256, 1])
        c2 = np.array([188 / 256, 245 / 256, 66 / 256, 1])
        c3 = np.array([108 / 256, 201 / 256, 46 / 256, 1])
        c4 = np.array([82 / 256, 138 / 256, 45 / 256, 1])
        c5 = np.array([24 / 256, 110 / 256, 45 / 256, 1])
        cm = LinearSegmentedColormap.from_list(
            "custom", [c0, c1, c2, c3, c4, c5], N=total
        )
        df_cyclic.sort_values(by="number", inplace=True)
        for idx in range(len(df_cyclic)):
            try:
                color = rgb2hex(cm(df_cyclic["number"][idx] / total))
                prod = pd.DataFrame(df_cyclic["prod"][idx])
                prod = prod / 30.45
                fig_cyclic_jobs.add_trace(
                    go.Scatter(
                        x=prod.index,
                        y=prod["oil"] - prod["oil"].loc["0"],
                        name=df_cyclic["start"][idx][:10],
                        mode="lines",
                        line=dict(
                            color=color, shape="spline", smoothing=0.3, width=3
                        ),
                        legendgroup=str(df_cyclic["number"][idx]),
                    ),
                    row=1,
                    col=1,
                )
                fig_cyclic_jobs.add_trace(
                    go.Scatter(
                        x=[df_cyclic["total"][idx]],
                        y=[prod["oil"].loc["1"] - prod["oil"].loc["-1"]],
                        name=df_cyclic["start"][idx][:10],
                        mode="markers",
                        marker=dict(color=color, size=10),
                        legendgroup=str(df_cyclic["number"][idx]),
                        showlegend=False,
                    ),
                    row=2,
                    col=1,
                )
            except Exception:
                pass

        fig_cyclic_jobs.update_xaxes(title_text="Month", row=1, col=1)
        fig_cyclic_jobs.update_xaxes(
            title_text="Cyclic Volume (bbls)", row=2, col=1
        )
        fig_cyclic_jobs.update_yaxes(
            title_text="Incremental Oil (bbls)", row=1, col=1
        )
        fig_cyclic_jobs.update_yaxes(
            title_text="Incremental Oil (bbls)", row=2, col=1
        )

        fig_cyclic_jobs.update_layout(
            margin={"l": 0, "t": 0, "b": 0, "r": 0},
            font=dict(family="Roboto Mono"),
        )

        graphJSON_cyclic_jobs = json.dumps(
            fig_cyclic_jobs, cls=plotly.utils.PlotlyJSONEncoder
        )
    except Exception:
        graphJSON_cyclic_jobs = None
    client.close()
    return graphJSON_cyclic_jobs


def get_header_oilgas(api):
    client = MongoClient(os.environ["MONGODB_CLIENT"])
    db = client.petroleum
    docs = db.doggr.find(
        {"api": api}, {"cyclic_jobs": 0, "prodinj": 0, "crm": 0}
    )
    for x in docs:
        header = dict(x)
    try:
        header.pop("_id")
    except Exception:
        pass

    for k, v in header.items():
        try:
            if math.isnan(v):
                header[k] = 0
            else:
                header[k] = v
        except Exception:
            pass

    client.close()
    return header


def get_header_tags_oilgas(tags):
    client = MongoClient(os.environ["MONGODB_CLIENT"])
    db = client.petroleum
    docs = db.doggr.find(
        {"tags": {"$in": tags}}, {"cyclic_jobs": 0, "prodinj": 0, "crm": 0}
    )
    headers = []
    for x in docs:
        header = dict(x)
        try:
            header.pop("_id")
        except Exception:
            pass
        headers.append(header)
    client.close()
    return headers


def get_tags_oilgas(api):
    client = MongoClient(os.environ["MONGODB_CLIENT"])
    db = client.petroleum
    docs = db.doggr.find({"api": api}, {"tags": 1})
    for x in docs:
        tags = dict(x)
    taglist = []
    try:
        for val in tags["tags"]:
            taglist.append({"id": val, "name": val})
        client.close()
    except Exception:
        pass
    return taglist


def set_tags_oilgas(api, tags):
    client = MongoClient(os.environ["MONGODB_CLIENT"])
    db = client.petroleum
    db.doggr.update(
        {"api": api}, {"$set": {"tags": tags}}, upsert=False, multi=False
    )


def get_graph_oilgas(api, axis):
    client = MongoClient(os.environ["MONGODB_CLIENT"])
    db = client.petroleum
    try:
        df = get_prodinj([api])

        data = [
            go.Scatter(
                x=df["date"],
                y=df["oil"],
                name="oil",
                line=dict(
                    color="#50bf37", shape="spline", smoothing=0.3, width=3
                ),
                mode="lines",
            ),
            go.Scatter(
                x=df["date"],
                y=df["water"],
                name="water",
                line=dict(
                    color="#4286f4", shape="spline", smoothing=0.3, width=3
                ),
                mode="lines",
            ),
            go.Scatter(
                x=df["date"],
                y=df["gas"],
                name="gas",
                line=dict(
                    color="#ef2626", shape="spline", smoothing=0.3, width=3
                ),
                mode="lines",
            ),
            go.Scatter(
                x=df["date"],
                y=df["steam"],
                name="steam",
                line=dict(
                    color="#e32980", shape="spline", smoothing=0.3, width=3
                ),
                mode="lines",
            ),
            go.Scatter(
                x=df["date"],
                y=df["cyclic"],
                name="cyclic",
                line=dict(
                    color="#fcd555", shape="spline", smoothing=0.3, width=3
                ),
                mode="lines",
            ),
            go.Scatter(
                x=df["date"],
                y=df["water_i"],
                name="water_inj",
                line=dict(
                    color="#03b6fc", shape="spline", smoothing=0.3, width=3
                ),
                mode="lines",
            ),
            go.Scatter(
                x=df["date"],
                y=df["gasair"],
                name="gasair",
                line=dict(
                    color="#fc7703", shape="spline", smoothing=0.3, width=3
                ),
                mode="lines",
            ),
            go.Scatter(
                x=df["date"],
                y=df["oilgrav"],
                name="oilgrav",
                visible="legendonly",
                line=dict(
                    color="#81d636", shape="spline", smoothing=0.3, width=3
                ),
                mode="lines",
            ),
            go.Scatter(
                x=df["date"],
                y=df["pcsg"],
                name="pcsg",
                visible="legendonly",
                line=dict(
                    color="#4136d6", shape="spline", smoothing=0.3, width=3
                ),
                mode="lines",
            ),
            go.Scatter(
                x=df["date"],
                y=df["ptbg"],
                name="ptbg",
                visible="legendonly",
                line=dict(
                    color="#7636d6", shape="spline", smoothing=0.3, width=3
                ),
                mode="lines",
            ),
            go.Scatter(
                x=df["date"],
                y=df["btu"],
                name="btu",
                visible="legendonly",
                line=dict(
                    color="#d636d1", shape="spline", smoothing=0.3, width=3
                ),
                mode="lines",
            ),
            go.Scatter(
                x=df["date"],
                y=df["pinjsurf"],
                name="pinjsurf",
                visible="legendonly",
                line=dict(
                    color="#e38f29", shape="spline", smoothing=0.3, width=3
                ),
                mode="lines",
            ),
        ]

        if axis == "log":
            layout = go.Layout(
                autosize=True,
                font=dict(family="Roboto Mono"),
                hovermode="closest",
                hoverlabel=dict(font=dict(family="Roboto Mono")),
                showlegend=True,
                legend=dict(orientation="h"),
                yaxis=dict(type="log"),
                uirevision=True,
                margin=dict(r=50, t=30, b=30, l=60, pad=0),
            )
        else:
            layout = go.Layout(
                autosize=True,
                font=dict(family="Roboto Mono"),
                hovermode="closest",
                hoverlabel=dict(font=dict(family="Roboto Mono")),
                showlegend=True,
                legend=dict(orientation="h"),
                uirevision=True,
                margin=dict(r=50, t=30, b=30, l=60, pad=0),
            )
        graphJSON = json.dumps(
            dict(data=data, layout=layout), cls=plotly.utils.PlotlyJSONEncoder
        )
    except Exception:
        graphJSON = None
    client.close()
    return graphJSON


def set_decline_oilgas(api):
    dca.decline_curve(str(api))


def get_decline_oilgas(api, axis):
    client = MongoClient(os.environ["MONGODB_CLIENT"])
    db = client.petroleum
    try:
        docs = db.doggr.find({"api": str(api)}, {"prodinj": 1, "decline": 1})
        for x in docs:
            doc = dict(x)
        prodinj = pd.DataFrame(doc["prodinj"])
        try:
            decline = pd.DataFrame(doc["decline"])
        except Exception:
            pass

        prodinj = prodinj.sort_values(by="date")

        start = pd.to_datetime(prodinj["date"].max())
        end = pd.to_datetime(prodinj["date"].max()) + np.timedelta64(48, "M")

        def model_func(t, qi, d, b):
            if b == 0:
                b = 1e-9
            return qi / ((1 + b * d * t) ** (1 / b))

        forecasts = pd.DataFrame(
            index=pd.date_range(start=start, end=end, freq="MS"),
            columns=["oil", "water", "gas"],
        )
        forecasts["date"] = forecasts.index

        prodinj = prodinj[["date", "oil", "water", "gas"]]

        prodinj = pd.concat(
            [prodinj[["date", "oil", "water", "gas"]], forecasts],
            sort=True,
            axis=0,
        )
        prodinj["date"] = pd.to_datetime(prodinj["date"])
        prodinj.index = prodinj["date"]
        prodinj = prodinj.drop_duplicates(subset=["date"])

        try:
            prodinj["oil_fc"] = prodinj["date"]
            prodinj["oil_fc"] = prodinj["oil_fc"].apply(
                lambda row: model_func(
                    int(
                        (
                            (
                                row
                                - pd.to_datetime(
                                    decline["oil"]["decline_start"]
                                )
                            )
                            / np.timedelta64(1, "M")
                        )
                    ),
                    decline["oil"]["qi"],
                    decline["oil"]["d"],
                    decline["oil"]["b"],
                )
            )
            prodinj["oil_fc"] = prodinj["oil_fc"] * 30.45
            prodinj.loc[
                prodinj["date"] < decline["oil"]["decline_start"], "oil_fc"
            ] = prodinj["oil"]
        except Exception:
            pass

        try:
            prodinj["oilcut"] = prodinj["oil"] / (
                prodinj["water"] + prodinj["oil"]
            )
            prodinj["oilcut_fc"] = prodinj["date"]
            prodinj["oilcut_fc"] = prodinj["oilcut_fc"].apply(
                lambda row: model_func(
                    int(
                        (
                            (
                                row
                                - pd.to_datetime(
                                    decline["oilcut"]["decline_start"]
                                )
                            )
                            / np.timedelta64(1, "M")
                        )
                    ),
                    decline["oilcut"]["qi"],
                    decline["oilcut"]["d"],
                    decline["oilcut"]["b"],
                )
            )
            prodinj.loc[
                prodinj["date"] < decline["oilcut"]["decline_start"],
                "oilcut_fc",
            ] = prodinj["oilcut"]
        except Exception:
            pass

        try:
            prodinj["water_fc"] = prodinj["date"]
            prodinj["water_fc"] = prodinj["water_fc"].apply(
                lambda row: model_func(
                    int(
                        (
                            (
                                row
                                - pd.to_datetime(
                                    decline["water"]["decline_start"]
                                )
                            )
                            / np.timedelta64(1, "M")
                        )
                    ),
                    decline["water"]["qi"],
                    decline["water"]["d"],
                    decline["water"]["b"],
                )
            )
            prodinj["water_fc"] = prodinj["water_fc"] * 30.45
            prodinj.loc[
                prodinj["date"] < decline["water"]["decline_start"], "water_fc"
            ] = prodinj["water"]
        except Exception:
            pass

        try:
            prodinj["gas_fc"] = prodinj["date"]
            prodinj["gas_fc"] = prodinj["gas_fc"].apply(
                lambda row: model_func(
                    int(
                        (
                            (
                                row
                                - pd.to_datetime(
                                    decline["gas"]["decline_start"]
                                )
                            )
                            / np.timedelta64(1, "M")
                        )
                    ),
                    decline["gas"]["qi"],
                    decline["gas"]["d"],
                    decline["gas"]["b"],
                )
            )
            prodinj["gas_fc"] = prodinj["gas_fc"] * 30.45
            prodinj.loc[
                prodinj["date"] < decline["gas"]["decline_start"], "gas_fc"
            ] = prodinj["gas"]
        except Exception:
            pass

        data = []
        data_cum = []

        try:
            data.append(
                go.Scatter(
                    x=prodinj["date"],
                    y=prodinj["oil"] / 30.45,
                    name="oil",
                    line=dict(
                        color="#50bf37", shape="spline", smoothing=0.3, width=3
                    ),
                    mode="lines",
                )
            )
        except Exception:
            pass

        try:
            data.append(
                go.Scatter(
                    x=prodinj["date"],
                    y=prodinj["oil_fc"] / 30.45,
                    name="oil_fc",
                    line=dict(
                        color="#50bf37",
                        shape="spline",
                        dash="dot",
                        smoothing=0.3,
                        width=3,
                    ),
                    mode="lines",
                ),
            )
        except Exception:
            pass

        try:
            data_cum.append(
                go.Scatter(
                    x=prodinj["oil"].cumsum(),
                    y=prodinj["oil"] / 30.45,
                    name="oil",
                    line=dict(
                        color="#50bf37", shape="spline", smoothing=0.3, width=3
                    ),
                    mode="lines",
                )
            )
        except Exception:
            pass

        try:
            data_cum.append(
                go.Scatter(
                    x=prodinj["oil_fc"].cumsum(),
                    y=prodinj["oil_fc"] / 30.45,
                    name="oil_fc",
                    line=dict(
                        color="#50bf37",
                        shape="spline",
                        dash="dot",
                        smoothing=0.3,
                        width=3,
                    ),
                    mode="lines",
                ),
            )
        except Exception:
            pass

        try:
            data.append(
                go.Scatter(
                    x=prodinj["date"],
                    y=prodinj["oilcut"],
                    name="oilcut",
                    line=dict(
                        color="#2EF4D6", shape="spline", smoothing=0.3, width=3
                    ),
                    mode="lines",
                )
            )
        except Exception:
            pass

        try:
            data.append(
                go.Scatter(
                    x=prodinj["date"],
                    y=prodinj["oilcut_fc"],
                    name="oilcut_fc",
                    line=dict(
                        color="#2EF4D6",
                        shape="spline",
                        dash="dot",
                        smoothing=0.3,
                        width=3,
                    ),
                    mode="lines",
                ),
            )
        except Exception:
            pass

        try:
            data_cum.append(
                go.Scatter(
                    x=prodinj["oil"].cumsum(),
                    y=prodinj["oilcut"],
                    name="oilcut",
                    line=dict(
                        color="#2EF4D6", shape="spline", smoothing=0.3, width=3
                    ),
                    mode="lines",
                )
            )
        except Exception:
            pass

        try:
            data_cum.append(
                go.Scatter(
                    x=prodinj["oil"].cumsum(),
                    y=prodinj["oilcut_fc"],
                    name="oilcut_fc",
                    line=dict(
                        color="#2EF4D6",
                        shape="spline",
                        dash="dot",
                        smoothing=0.3,
                        width=3,
                    ),
                    mode="lines",
                ),
            )
        except Exception:
            pass

        try:
            data.append(
                go.Scatter(
                    x=prodinj["date"],
                    y=prodinj["water"] / 30.45,
                    name="water",
                    line=dict(
                        color="#4286f4", shape="spline", smoothing=0.3, width=3
                    ),
                    mode="lines",
                )
            )
        except Exception:
            pass

        try:
            data.append(
                go.Scatter(
                    x=prodinj["date"],
                    y=prodinj["water_fc"] / 30.45,
                    name="water_fc",
                    line=dict(
                        color="#4286f4",
                        shape="spline",
                        dash="dot",
                        smoothing=0.3,
                        width=3,
                    ),
                    mode="lines",
                )
            )
        except Exception:
            pass

        try:
            data_cum.append(
                go.Scatter(
                    x=prodinj["water"].cumsum(),
                    y=prodinj["water"] / 30.45,
                    name="water",
                    line=dict(
                        color="#4286f4", shape="spline", smoothing=0.3, width=3
                    ),
                    mode="lines",
                )
            )
        except Exception:
            pass

        try:
            data_cum.append(
                go.Scatter(
                    x=prodinj["water_fc"].cumsum(),
                    y=prodinj["water_fc"] / 30.45,
                    name="water_fc",
                    line=dict(
                        color="#4286f4",
                        shape="spline",
                        dash="dot",
                        smoothing=0.3,
                        width=3,
                    ),
                    mode="lines",
                ),
            )
        except Exception:
            pass

        try:
            data.append(
                go.Scatter(
                    x=prodinj["date"],
                    y=prodinj["gas"] / 30.45,
                    name="gas",
                    line=dict(
                        color="#ef2626", shape="spline", smoothing=0.3, width=3
                    ),
                    mode="lines",
                )
            )
        except Exception:
            pass

        try:
            data.append(
                go.Scatter(
                    x=prodinj["date"],
                    y=prodinj["gas_fc"] / 30.45,
                    name="gas_fc",
                    line=dict(
                        color="#ef2626",
                        shape="spline",
                        dash="dot",
                        smoothing=0.3,
                        width=3,
                    ),
                    mode="lines",
                )
            )
        except Exception:
            pass

        try:
            data_cum.append(
                go.Scatter(
                    x=prodinj["gas"].cumsum(),
                    y=prodinj["gas"] / 30.45,
                    name="gas",
                    line=dict(
                        color="#ef2626", shape="spline", smoothing=0.3, width=3
                    ),
                    mode="lines",
                )
            )
        except Exception:
            pass

        try:
            data_cum.append(
                go.Scatter(
                    x=prodinj["gas_fc"].cumsum(),
                    y=prodinj["gas_fc"] / 30.45,
                    name="gas_fc",
                    line=dict(
                        color="#ef2626",
                        shape="spline",
                        dash="dot",
                        smoothing=0.3,
                        width=3,
                    ),
                    mode="lines",
                ),
            )
        except Exception:
            pass

        if axis == "log":
            layout = go.Layout(
                autosize=True,
                font=dict(family="Roboto Mono"),
                hovermode="closest",
                hoverlabel=dict(font=dict(family="Roboto Mono")),
                showlegend=True,
                legend=dict(orientation="h"),
                yaxis=dict(type="log"),
                uirevision=True,
                margin=dict(r=50, t=30, b=30, l=60, pad=0),
            )
        else:
            layout = go.Layout(
                autosize=True,
                font=dict(family="Roboto Mono"),
                hovermode="closest",
                hoverlabel=dict(font=dict(family="Roboto Mono")),
                showlegend=True,
                legend=dict(orientation="h"),
                uirevision=True,
                margin=dict(r=50, t=30, b=30, l=60, pad=0),
            )
        graphJSON = json.dumps(
            dict(data=data, layout=layout), cls=plotly.utils.PlotlyJSONEncoder
        )
        graphJSON_cum = json.dumps(
            dict(data=data_cum, layout=layout),
            cls=plotly.utils.PlotlyJSONEncoder,
        )
    except Exception:
        graphJSON = None
        graphJSON_cum = None
    client.close()
    return graphJSON, graphJSON_cum
