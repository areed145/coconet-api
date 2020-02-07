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
    noverlap = int(nperseg-1)

    f, t, Sxx = signal.stft(
        df_s['state'], window='blackmanharris', nperseg=nperseg, noverlap=noverlap, fs=fs, #detrend='constant'
        #     df_s['state'], window='hanning', mode='magnitude', nperseg=nperseg, noverlap=noverlap, fs=fs
    )

    Sxx = np.abs(Sxx)

    data_spectro.append(
        go.Heatmap(
            x=t,
            y=f,
            z=Sxx,
            name=sensor,
            colorscale='Portland',
            showscale=False,
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

    df_s = df
    df_s.index = pd.to_datetime(df_s['timestamp_'])
    df_s['state'] = df_s['state'].astype(float)
    df_s = df_s[['state']].resample('1T').mean()
    df_s = df_s.interpolate()

    fs = 1/60
    nperseg = np.minimum(len(df_s['state']), 128)
    noverlap = int(nperseg-1)

    f, t, Sxx = signal.stft(
        df_s['state'], window='blackmanharris', nperseg=nperseg, noverlap=noverlap, fs=fs, #detrend='constant'
        #     df_s['state'], window='hanning', mode='magnitude', nperseg=nperseg, noverlap=noverlap, fs=fs
    )

    Sxx = np.abs(Sxx)
    # Sxx = np.log(Sxx)

    scaler = preprocessing.MinMaxScaler()

    ntrain = int(len(Sxx.T)/2)

    X = pd.DataFrame(
        Sxx.T,
        index=t
    )

    X_train = scaler.fit_transform(X.iloc[:ntrain, :])

    X_test = scaler.transform(X.iloc[ntrain:, :])

    pca = PCA(n_components=2, svd_solver='full')

    X_train_pca = pca.fit_transform(X_train)
    X_train_pca = pd.DataFrame(X_train_pca)
    X_train_pca.index = X.iloc[:ntrain, :].index

    X_test_pca = pca.transform(X_test)
    X_test_pca = pd.DataFrame(X_test_pca)
    X_test_pca.index = X.iloc[ntrain:, :].index

    data_train = np.array(X_train_pca.values)
    data_test = np.array(X_test_pca.values)

    cov_mx, inv_cov_mx = cov_matrix(data_train)

    mean_distr = data_train.mean(axis=0)

    dist_test = mahalanobis_dist(
        inv_cov_mx, mean_distr, data_test, verbose=False)
    dist_train = mahalanobis_dist(
        inv_cov_mx, mean_distr, data_train, verbose=False)

    dist_all = np.concatenate([dist_train, dist_test], axis=0)
    thresh = md_threshold(dist_all)

    df_s['dist'] = dist_all[:len(df_s)]
    df_s['thresh'] = thresh

    data = []
    data_anom = []
    # data_hm = []

    data.append(
        go.Scatter(
            x=df_s.index,
            y=df_s['state'],
            name=sensor,
            line=dict(
                # color='#e3a622',
                shape='spline',
                smoothing=0.7,
                width=3
            ),
            mode='lines'
        )
    )
    data.append(
        go.Scatter(
            x=df_s[df_s['dist'] > thresh].index,
            y=df_s[df_s['dist'] > thresh]['state'],
            name='anomalies',
            marker=dict(
                color='#eb2369'
            ),
            mode='markers'
        )
    )
    data_anom.append(
        go.Scatter(
            x=df_s.index,
            y=df_s['dist'],
            name=sensor,
            line=dict(
                color='#4823eb',
                shape='spline',
                smoothing=0.7,
                width=3
            ),
            mode='lines'
        )
    )
    data_anom.append(
        go.Scatter(
            x=df_s.index,
            y=df_s['thresh'],
            name='threshold',
            line=dict(
                color='#de1b4f',
                shape='spline',
                smoothing=0.7,
                width=3
            ),
            mode='lines'
        )
    )
    data_anom.append(
        go.Scatter(
            x=df_s[df_s['dist'] > thresh].index,
            y=df_s[df_s['dist'] > thresh]['dist'],
            name='anomalies',
            line=dict(
                color='#de1b4f',
                shape='spline',
                smoothing=0.7,
                width=3
            ),
            mode='markers'
        )
    )

    # data_hm.append(
    #     go.Heatmap(
    #         x=t,
    #         y=f,
    #         z=Sxx,
    #         name=sensor,
    #         colorscale='Viridis',
    #     )
    # )

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

    # layout_hm = go.Layout(
    #     autosize=True,
    #     font=dict(family='Ubuntu'),
    #     showlegend=False,
    #     # legend=dict(orientation='h'),
    #     xaxis=dict(range=[start, now]),
    #     hovermode='closest',
    #     hoverlabel=dict(font=dict(family='Ubuntu')),
    #     uirevision=True,
    #     margin=dict(r=50, t=30, b=30, l=60, pad=0),
    # )

    try:
        graphJSON = json.dumps(dict(data=data, layout=layout),
                               cls=plotly.utils.PlotlyJSONEncoder)
        graphJSON_anom = json.dumps(dict(data=data_anom, layout=layout),
                                    cls=plotly.utils.PlotlyJSONEncoder)
        # graphJSON_hm = json.dumps(dict(data=data_hm, layout=layout),
        #                           cls=plotly.utils.PlotlyJSONEncoder)
    except:
        graphJSON = None
        graphJSON_anom = None
        # graphJSON_hm = None

    client.close()
    return graphJSON, graphJSON_anom
