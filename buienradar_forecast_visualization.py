import base64
import io
import json
import zipfile
from collections import defaultdict
from datetime import datetime as dt

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pandas.tseries.offsets import BDay
import matplotlib.colors as mcolors


pd.set_option('display.max_colwidth', None)


def tag(the_tag, txt, attributes=''):
    return '<{tag}{attributes}>{txt}</{tag}>'.format(tag=the_tag, txt=txt,
            attributes=(('' if attributes == '' else ' ') + attributes))


def get_chart_image_stream(h4):
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close(plt.gcf())
    encoded = base64.b64encode(buf.getvalue())
    return tag('h4', h4) + '<img src="data:image/png;base64,{}">'.format(encoded.decode("utf-8"))


def diff_month(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month


def tick_freq(plot_, freq):
    for label in plot_.get_xticklabels():
        if np.int(label.get_text()) % freq == 0:
            label.set_visible(True)
        else:
            label.set_visible(False)


def str_bd_offset(i):
    return (dt.now() - BDay(i)).strftime('%Y%m%d')


nl = '\n'


class ForecastVizualization():

    def __init__(self):
        self.zip_file = fr'results/forecasts.zip'
        # self.zip_file = fr'c:\data\forecasts.zip'

    def store_item(self, k, v, day):
        self.days[k][day.get('datetime')].append([self.ts, v])

    def get_days(self):
        self.days = defaultdict(lambda: defaultdict(list))
        self.forecasts = zipfile.ZipFile(self.zip_file, 'r')
        for file in self.forecasts.namelist():
            data = json.load(self.forecasts.open(file))
            self.ts = data.get('timestamp')
            v = [[self.store_item(k, v, day) for k, v in day.items() if not isinstance(v, (dict, list))]
                 for day in data['days']]

    def handle_sub_key(self, kk, v, k):
        if isinstance(v, list) and not k == 'datetime':
            df_w = pd.DataFrame(v, columns=['ts', k])
            for row in df_w.iterrows():
                self.df_hm.loc[kk, row[1][0]] = row[1][1]
        else:
            return v

    def handle_key(self, k):
        self.category = k
        self.df_hm = pd.DataFrame()
        self.chart_data = [(f'{kk}: {self.handle_sub_key(kk, v, k)} ') for kk, v in self.days[k].items()]

    def get_rvb(self, category):
        clist = {'temperature': [(0, "blue"), (.2, "lightblue"), (.35, "green"), (.55, "yellow"), (.7,                      "orange"),(.8, "red"), (1, "purple")],
                 'maxtemperature': [(0, "blue"), (.2, "lightblue"), (.35, "green"), (.55, "yellow"), (.7,                   "orange"), (.8, "red"), (1, "purple")],
                 'mintemperature': [(0, "blue"), (.2, "lightblue"), (.35, "green"), (.55, "yellow"), (.7,                   "orange"), (.8, "red"), (1, "purple")],
                 'humidity': [(0, "lightblue"), (.2, "blue"), (.35, "green"), (.55, "yellow"), (.7,                         "orange"), (.8, "red"), (1, "purple")],
                 'windspeedms': [(0, "lightblue"), (.2, "blue"), (.35, "green"), (.55, "yellow"), (.7,                      "orange"), (.8, "red"), (1, "purple")],
                 'sunshine': [(0, "white"), (.50, "grey"), (1, "yellow")],
                 'pollenindex': [(0, "green"), (.25, "lightblue"), (.35, "blue"), (.5, "yellow"), (.7,                      "orange"), (.8, "red"), (1, "purple")],
                 'precipitationmm': [(0, "white"), (.001, "white"), (.01, "lightblue"), (.2, "blue"), (.35,                 "green"), (.55, "yellow"), (.7, "orange"), (.8, "red"), (1, "purple")],
                 'precipitation': [(0, "white"), (.01, "white"), (.2, "lightblue"), (.35, "green"), (.55,                   "yellow"), (.7, "orange"), (.8, "red"), (1, "purple")],
                 'beaufort': [(0, "blue"), (.2, "lightblue"), (.35, "green"), (.55, "yellow"), (.7,                         "orange"), (.8, "red"), (1, "purple")]}
        return mcolors.LinearSegmentedColormap.from_list("", clist[category])

    def min_max(self, category):
        return {'temperature': (-10, 40), 'humidity': (0, 100), 'beaufort': (0, 12),
                'precipitation': (0, 10), 'precipitationmm': (0, 100), 'sunshine': (0, 100),
                'pollenindex': (0, 10), 'maxtemperature': (-10, 40),
                'mintemperature': (-10, 40), 'windspeedms': (0, 100)}[category]

    def set_annotations(self, ax, df):
        for i in range(len(df)):
            for j in range(len(df.columns)):
                if not str(df.iloc[i, j]) == str(np.nan):
                    text = ax.text(j, i, df.iloc[i, j], ha="center", va="center",
                                   color="black", fontsize=4)

    def set_ticks(self, ax, df):
        # We want to show all ticks...
        ax.set_xticks(np.arange(len(df.columns)))
        ax.set_yticks(np.arange(len(df)))
        # ... and label them with the respective list entries
        ax.set_xticklabels([d.split('T')[0] for d in df.columns])
        ax.set_yticklabels([d.split('T')[0] for d in df.index])
        #     ax.xaxis.set_ticks_position("top")
        plt.setp(ax.get_xticklabels(), rotation=90, ha="right", rotation_mode="anchor")

    def visualize_category(self, category):
        self.handle_key(category)
        first_day = (dt.today() - BDay(2)).strftime('%Y-%m-%dT%H:%M:%S')
        df_hm2 = self.df_hm[self.df_hm.index >= first_day]
        df_hm2 = df_hm2.dropna(how='all', axis=1).sort_index(axis=0).sort_index(axis=1, ascending=False)
        vmin, vmax = self.min_max(category)
        fig, ax = plt.subplots(figsize=(30, 30))
        im = ax.imshow(df_hm2, cmap=self.get_rvb(category), interpolation='nearest', vmin=vmin, vmax=vmax)
        self.set_annotations(ax, df_hm2)
        self.set_ticks(ax, df_hm2)
        plt.grid(alpha=.4)
        fig.tight_layout()
        fig.savefig(rf'results/bu_day_{category}.png')
        # fig.savefig(rf'c:\data\bu_day_{category}.png')

fv = ForecastVizualization()
fv.get_days()
fv.visualize_category('mintemperature')
fv.visualize_category('maxtemperature')
fv.visualize_category('precipitationmm')
