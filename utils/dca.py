import pandas as pd
import numpy as np
from pymongo import MongoClient
from datetime import date, datetime, timedelta, time
import json
import random
import os
import plotly.graph_objects as go
import scipy as sp
# import scipy.optimize
from scipy import stats
from bson import json_util


class decline_curve:

    def model_func(self, t, qi, d, b):
        return qi / ((1 + b * d * t) ** (1/b))

    def fit_exp_nonlinear(self, t, q, qi_max):
        opt_parms, parm_cov = sp.optimize.curve_fit(
            self.model_func, t, q, maxfev=10000, bounds=(0, [qi_max, 0.9, 1.]))
        qi, d, b = opt_parms
        return qi, d, b

    def average_sample(self, window, stream, lookback=None):
        vals_clean = self.streams[stream]['vals_clean']
        roll = vals_clean.rolling(
            window, center=True, win_type='triang').mean().dropna()
        roll = roll.interpolate()
        roll_dt = roll.diff().dropna()
        self.streams[stream]['roll'] = roll.copy(deep=True)
        self.streams[stream]['roll_dt'] = roll_dt.copy(deep=True)
        if lookback == None:
            lookback = roll_dt[roll_dt > 0][:-6].index.max()
        else:
            lookback = roll[lookback:-6].index.max()
        vals_use = vals_clean[vals_clean.index > lookback]
        nsamples = np.minimum(int(window / 2), int(len(vals_use) / 2))
        samples = vals_use.sample(nsamples)
        x = np.array(samples.index.astype(float)) - lookback
        y = samples.values
        qi = vals_use.dropna().mean()
        d = 0.01 + (random.randint(0, 1000)-500/1000)
        b = 0 + (random.randint(0, 1000)-500/1000)
        return qi, d, b, lookback

    def clean_sample(self, stream):
        self.streams[stream] = {}
        if stream == 'fluid':
            vals = (self.prodinj['oil'] + self.prodinj['water']) / 30.45
        elif stream == 'owr':
            vals = self.prodinj['oil'] / self.prodinj['water']
        elif stream == 'oilcut':
            vals = self.prodinj['oil'] / \
                (self.prodinj['oil'] + self.prodinj['water'])
        elif stream == 'oilcut_gas':
            vals = self.prodinj['oil'] / \
                (self.prodinj['oil'] + self.prodinj['gas'])
        else:
            vals = (self.prodinj[stream]) / 30.45
        vals.index = vals.index.astype(int)
        vals = vals.replace(0, pd.np.nan)
        vals_clean = vals.copy(deep=True)
        vals_outliers = vals.copy(deep=True)
        p01 = vals.quantile(0.01)
        p99 = vals.quantile(0.99)
        vals_clean.loc[(vals_clean > p99) | (vals_clean < p01)] = pd.np.nan
        vals_outliers.loc[(vals_outliers < p99) & (
            vals_outliers > p01)] = pd.np.nan
        self.streams[stream]['vals_clean'] = vals_clean
        self.streams[stream]['vals_outliers'] = vals_outliers
        vals_clean = vals_clean.dropna()
#         vals_clean = vals_clean.interpolate()
        self.streams[stream]['vals'] = vals
        self.streams[stream]['vals_clean'] = vals_clean
        if vals_clean.sum() > 0:
            return True
        else:
            return False

    def decline_sample(self, window, stream, lookback=None):
        vals_clean = self.streams[stream]['vals_clean']
        roll = vals_clean.rolling(
            window, center=True, win_type='triang').mean().dropna()
        roll = roll.interpolate()
        roll_dt = roll.diff().dropna()
        self.streams[stream]['roll'] = roll.copy(deep=True)
        self.streams[stream]['roll_dt'] = roll_dt.copy(deep=True)
        if lookback == None:
            lookback = roll_dt[roll_dt > 0][:-6].index.max()
        else:
            lookback = roll[lookback:-6].index.max()
        vals_use = vals_clean[vals_clean.index > lookback]
        qi_max = vals_use.max()
        nsamples = np.minimum(int(window / 2), int(len(vals_use) / 2))
        samples = vals_use.sample(nsamples)
        x = np.array(samples.index.astype(float)) - lookback
        y = samples.values
        qi, d, b = self.fit_exp_nonlinear(x, y, qi_max)
        return qi, d, b, lookback

    def get_most_likely(self, stream):
        params = {}
        values = self.streams[stream]['iters'].T.values
        kde = stats.gaussian_kde(values)
        density = kde(values)
        self.streams[stream]['iters']['density'] = density
        df_ = self.streams[stream]['iters'][self.streams[stream]['iters']
                                            ['density'] == self.streams[stream]['iters']['density'].max()]
        for col in self.streams[stream]['iters'].columns:
            params[col] = df_[col].values[0]
        self.streams[stream]['params'] = params
        self.streams[stream]['params']['decline_start'] = self.prodinj['date'][self.streams[stream]
                                                                               ['params']['lookback']]
        self.params[stream] = params
        self.params[stream]['decline_start'] = self.prodinj['date'][self.streams[stream]
                                                                    ['params']['lookback']]

    def decline_curve(self, stream, lookback_use=None):
        print(stream)
        vol_flag = self.clean_sample(stream)
        if vol_flag == True:
            qis = []
            ds = []
            bs = []
            lookbacks = []
            exp = 2
            success = False
            while success == False:
                for i in range(2*(10**exp)):
                    window = random.randint(7, 301)
                    try:
                        qi, d, b, lookback = self.decline_sample(
                            window, stream, lookback_use)
                        qis.append(qi)
                        ds.append(d)
                        bs.append(b)
                        lookbacks.append(lookback)
                    except:
                        pass
                try:
                    df_ = pd.DataFrame()
                    df_['qi'] = qis
                    df_['d'] = ds
                    df_['b'] = bs
                    df_['lookback'] = lookbacks
                    print(len(df_))
                    self.streams[stream]['iters'] = df_
                    self.get_most_likely(stream=stream)
                    print(self.streams[stream]['params'])
                    success = True
                except:
                    if exp == 4:
                        print('averaging')
                        qis = []
                        ds = []
                        bs = []
                        lookbacks = []
                        for i in range(100):
                            window = random.randint(7, 301)
                            qi, d, b, lookback = self.average_sample(
                                window, stream, lookback_use)
                            qis.append(qi)
                            ds.append(d)
                            bs.append(b)
                            lookbacks.append(lookback)
                        df_ = pd.DataFrame()
                        df_['qi'] = qis
                        df_['d'] = ds
                        df_['b'] = bs
                        df_['lookback'] = lookbacks
                        print(len(df_))
                        self.streams[stream]['iters'] = df_
                        break
                    else:
                        exp += 1

    def get_prodinj(self):
        client = MongoClient(os.environ['MONGODB_CLIENT'])
        db = client.petroleum
        docs = db.doggr.find({'api': self.api}, {'prodinj': 1})
        for x in docs:
            doc = dict(x)
        self.prodinj = pd.DataFrame(doc['prodinj'])
        client.close()

    def write_declines(self):
        params = self.params
        for dict_value in params.keys():
            for v in params[dict_value]:
                try:
                    params[dict_value][v] = float(
                        round(params[dict_value][v], 3))
                except:
                    pass
                if isinstance(v, np.bool_):
                    params[dict_value][v] = bool(v)

                if isinstance(v, np.int64):
                    params[dict_value][v] = int(v)

                if isinstance(v, np.float64):
                    params[dict_value][v] = float(v)
        client = MongoClient(os.environ['MONGODB_CLIENT'])
        db = client.petroleum
        db.doggr.update_one({'api': self.api}, {
                            '$set': {'decline': params}}, upsert=False)
        print(self.api, ' written')
        client.close()

    def __init__(self, api):
        self.api = api
        self.get_prodinj()
        self.streams = {}
        self.params = {}
        self.decline_curve(stream='oil')
#         lookback_use = self.streams[stream]['params']['lookback']
        lookback_use = None
        self.decline_curve(stream='oilcut', lookback_use=lookback_use)
        self.decline_curve(stream='water')
        self.decline_curve(stream='gas')
        self.write_declines()
