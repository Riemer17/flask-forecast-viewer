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

pd.set_option('display.max_colwidth', -1)


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

        print(self.days)


fv = ForecastVizualization()
fv.get_days()
