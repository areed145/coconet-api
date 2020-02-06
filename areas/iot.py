import os
import numpy as np
import pandas as pd
from pymongo import MongoClient
import plotly
import plotly.graph_objs as go
import json
from datetime import datetime, timedelta
from utils import config, helpers
from scipy import signal
from sklearn.decomposition import PCA
from sklearn import preprocessing


def create_graph_iot(sensor, time):
    client = MongoClient(os.environ['MONGODB_CLIENT'])
    start, now = helpers.get_time_range(time)
    db = client.iot
    df = pd.DataFrame(
        list(db.raw.find({'entity_id': {'$in': sensor}, 'timestamp_': {'$gt': start, '$lte': now}}).sort([('timestamp_', -1)])))
    if len(df) == 0:
        df = pd.DataFrame(list(db.raw.find(
            {'entity_id': {'$in': sensor}}).limit(2).sort([('timestamp_', -1)])))

    data = []
    for s in sensor:
        try:
            df_s = df[df['entity_id'] == s]
            data.append(
                go.Scatter(
                    x=df_s['timestamp_'],
                    y=df_s['state'],
                    name=s,
                    line=dict(
                        shape='spline',
                        smoothing=0.7,
                        width=3
                    ),
                    mode='lines'
                )
            )
        except:
            pass

    layout = go.Layout(
        autosize=True,
        colorway=config.colorway,
        font=dict(family='Ubuntu'),
        showlegend=True,
        legend=dict(orientation='h'),
        xaxis=dict(range=[start, now]),
        hovermode='closest',
        hoverlabel=dict(font=dict(family='Ubuntu')),
        uirevision=True,
        margin=dict(r=50, t=30, b=30, l=60, pad=0),
    )
    try:
        graphJSON = json.dumps(dict(data=data, layout=layout),
                               cls=plotly.utils.PlotlyJSONEncoder)
    except:
        graphJSON = None
    client.close()
    return graphJSON


def create_spectrogram_iot(sensor, time):
    client = MongoClient(os.environ['MONGODB_CLIENT'])
    start, now = helpers.get_time_range(time)
    db = client.iot
    df = pd.DataFrame(
        list(db.raw.find({'entity_id': sensor, 'timestamp_': {'$gt': start, '$lte': now}}).sort([('timestamp_', -1)])))
    if len(df) == 0:
        df = pd.DataFrame(list(db.raw.find(
            {'entity_id': sensor}).limit(2).sort([('timestamp_', -1)])))

    data = []
    data_spectro = []

    df_s = df
    df_s.index = pd.to_datetime(df_s['timestamp_'])
    df_s['state'] = df_s['state'].astype(float)
    df_s = df_s[['state']].resample('1T').mean()
    df_s = df_s.interpolate()
    data.append(
        go.Scatter(
            x=df_s.index,
            y=df_s['state'],
            name=sensor,
            line=dict(
                shape='spline',
                smoothing=0.7,
                width=3
            ),
            mode='lines'
        )
    )

    fs = 1/60
    nperseg = np.minimum(len(df_s['state']), 128)
    noverlap = int(7/8*nperseg)

    f, t, Sxx = signal.spectrogram(
        df_s['state'], window='hanning', mode='magnitude', nperseg=nperseg, noverlap=noverlap, fs=fs
    )

    data_spectro.append(
        go.Heatmap(
            x=t,
            y=f,
            z=np.log(Sxx),
            name=sensor,
            colorscale='Viridis',
        )
    )

    layout = go.Layout(
        autosize=True,
        colorway=config.colorway,
        font=dict(family='Ubuntu'),
        showlegend=True,
        legend=dict(orientation='h'),
        xaxis=dict(range=[start, now]),
        hovermode='closest',
        hoverlabel=dict(font=dict(family='Ubuntu')),
        uirevision=True,
        margin=dict(r=50, t=30, b=30, l=60, pad=0),
    )
    try:
        graphJSON = json.dumps(dict(data=data, layout=layout),
                               cls=plotly.utils.PlotlyJSONEncoder)
    except:
        graphJSON = None

    layout_spectro = go.Layout(
        autosize=True,
        font=dict(family='Ubuntu'),
        showlegend=False,
        # legend=dict(orientation='h'),
        xaxis=dict(range=[start, now]),
        hovermode='closest',
        hoverlabel=dict(font=dict(family='Ubuntu')),
        uirevision=True,
        margin=dict(r=50, t=30, b=30, l=60, pad=0),
    )

    graphJSON_spectro = json.dumps(dict(data=data_spectro, layout=layout_spectro),
                                   cls=plotly.utils.PlotlyJSONEncoder)

    client.close()
    return graphJSON, graphJSON_spectro


def cov_matrix(data, verbose=False):
    covariance_matrix = np.cov(data, rowvar=False)
    if is_pos_def(covariance_matrix):
        inv_covariance_matrix = np.linalg.inv(covariance_matrix)
        if is_pos_def(inv_covariance_matrix):
            return covariance_matrix, inv_covariance_matrix
        else:
            print("Error: Inverse of Covariance Matrix is not positive definite!")
    else:
        print("Error: Covariance Matrix is not positive definite!")


def mahalanobis_dist(inv_cov_matrix, mean_distr, data, verbose=False):
    inv_covariance_matrix = inv_cov_matrix
    vars_mean = mean_distr
    diff = data - vars_mean
    md = []
    for i in range(len(diff)):
        md.append(np.sqrt(diff[i].dot(inv_covariance_matrix).dot(diff[i])))
    return md


def md_detect_outliers(dist, extreme=False, verbose=False):
    k = 3. if extreme else 2.
    threshold = np.mean(dist) * k
    outliers = []
    for i in range(len(dist)):
        if dist[i] >= threshold:
            outliers.append(i)  # index of the outlier
    return np.array(outliers)


def md_threshold(dist, extreme=False, verbose=False):
    k = 3. if extreme else 2.
    threshold = np.mean(dist) * k
    return threshold


def is_pos_def(A):
    if np.allclose(A, A.T):
        try:
            np.linalg.cholesky(A)
            return True
        except np.linalg.LinAlgError:
            return False
    else:
        return False


def create_anomaly_iot(sensor, time):
    client = MongoClient(os.environ['MONGODB_CLIENT'])
    start, now = helpers.get_time_range(time)
    db = client.iot
    df = pd.DataFrame(
        list(db.raw.find({'entity_id': sensor, 'timestamp_': {'$gt': start, '$lte': now}}).sort([('timestamp_', -1)])))
    if len(df) == 0:
        df = pd.DataFrame(list(db.raw.find(
            {'entity_id': sensor}).limit(2).sort([('timestamp_', -1)])))

    data = []

    df_s = df
    df_s.index = pd.to_datetime(df_s['timestamp_'])
    df_s['state'] = df_s['state'].astype(float)
    df_s = df_s[['state']].resample('1T').mean()
    df_s = df_s.interpolate()

    fs = 1/60
    nperseg = np.minimum(len(df_s['state']), 128)
    noverlap = int(7/8*nperseg)
    ntrain = int(len(df_s['state'])/2)

    f, t, Sxx = signal.spectrogram(
        df_s['state'], window='hanning', mode='magnitude', nperseg=nperseg, noverlap=noverlap, fs=fs
    )

    scaler = preprocessing.MinMaxScaler()

    X_train = scaler.fit_transform(Sxx.T[:ntrain])

    X_test = scaler.transform(Sxx.T[ntrain:])

    pca = PCA(n_components=2, svd_solver='full')

    X_train_pca = pca.fit_transform(X_train)
    X_train_pca = pd.DataFrame(X_train_pca)
    X_train_pca.index = X_train.index

    X_test_pca = pca.transform(X_test)
    X_test_pca = pd.DataFrame(X_test_pca)
    X_test_pca.index = X_test.index

    data_train = np.array(X_train_pca.values)
    data_test = np.array(X_test_pca.values)

    cov_matrix, inv_cov_matrix = cov_matrix(data_train)

    mean_distr = data_train.mean(axis=0)

    dist_test = mahalanobis_dist(
        inv_cov_matrix, mean_distr, data_test, verbose=False)
    dist_train = mahalanobis_dist(
        inv_cov_matrix, mean_distr, data_train, verbose=False)
    threshold = md_threshold(dist_test, extreme=True)

    data.append(
        go.Scatter(
            x=df_s[:ntrain].index,
            y=df_s[:ntrain]['state'],
            name=sensor,
            line=dict(
                shape='spline',
                smoothing=0.7,
                width=3
            ),
            mode='lines'
        )
    )
    data.append(
        go.Scatter(
            x=df_s[ntrain:].index,
            y=df_s[ntrain:]['state'],
            name=sensor,
            line=dict(
                shape='spline',
                smoothing=0.7,
                width=3
            ),
            mode='lines'
        )
    )
    data.append(
        go.Scatter(
            x=df_s[ntrain:].index,
            y=threshold,
            name=sensor,
            line=dict(
                shape='spline',
                smoothing=0.7,
                width=3
            ),
            mode='lines'
        )
    )

    layout = go.Layout(
        autosize=True,
        colorway=config.colorway,
        font=dict(family='Ubuntu'),
        showlegend=True,
        legend=dict(orientation='h'),
        xaxis=dict(range=[start, now]),
        hovermode='closest',
        hoverlabel=dict(font=dict(family='Ubuntu')),
        uirevision=True,
        margin=dict(r=50, t=30, b=30, l=60, pad=0),
    )
    try:
        graphJSON = json.dumps(dict(data=data, layout=layout),
                               cls=plotly.utils.PlotlyJSONEncoder)
    except:
        graphJSON = None

    client.close()
    return graphJSON
