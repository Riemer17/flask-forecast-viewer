import base64
import io
import matplotlib.pyplot as plt
import json
import zipfile
import pandas as pd
from collections import defaultdict
from datetime import datetime as dt, timedelta
from flask import Flask, render_template

app = Flask(__name__)


class ForecastViz():

    def __init__(self):
        self.zip_file = fr'results/forecasts.zip'
        self.days = None

    def get_days(self):
        first_date = (dt.now() - timedelta(days=14)).strftime('%Y%m%d%H%M%S')
        self.days = defaultdict(lambda: defaultdict(list))
        self.forecasts = zipfile.ZipFile(self.zip_file, 'r')
        self.process_day_data(first_date)

    def process_day_data(self, first_date):
        for file in self.forecasts.namelist():
            if file > f'forecasts_{first_date}.json':
                data = json.load(self.forecasts.open(file))
                self.ts = data.get('timestamp')
                v = [[self.store_item(k, v, day) for k, v in day.items() if not isinstance(v, (dict, list))]
                     for day in data['days']]

    def store_item(self, k, v, day):
        self.days[k][day.get('datetime')].append([self.ts, v])

    def get_cats(self):
        # return ''.join([tag('tr', tag('td', k)) for k in self.days.keys()])
        return create_select(self.days.keys())


fv = ForecastViz()


def create_select(options, selected=0):
    action = 'window.location.href=this.value'
    options = '\n'.join([f'<option value={v}>{v}</option>' for v in options])
    return f'<select name="colour" method="GET" action="/" onchange=\'{action}\'>{options}</select>'


def create_img(field):
    return field


def get_chart_image_stream(h4):
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close(plt.gcf())
    encoded = base64.b64encode(buf.getvalue())
    return tag('h4', h4) + '<img src="data:image/png;base64,{}">'.format(encoded.decode("utf-8"))


def tag(the_tag, txt, attributes=''):
    return '<{tag}{attributes}>{txt}</{tag}>'.format(tag=the_tag, txt=txt,
           attributes=(('' if attributes == '' else ' ') + attributes))


def read_zip():
    first_date = (dt.now() - timedelta(days=14)).strftime('%Y%m%d%H%M%S')
    zip_name = r"resources/forecasts.zip"
    forecasts = zipfile.ZipFile(zip_name, 'r')
    return create_select([file for file in forecasts.namelist() if file > f'forecasts_{first_date}.json'])
    # return ''.join([tag('tr',tag('td', file)) for file in forecasts.namelist()
    #                 if file > f'forecasts_{first_date}.json'])

def insert_css():
    return open('static/style.css').read()


def handle_on_select(field, fv):
    if field in fv.days.keys():
        return create_select([f'fk_{field}_{k}' for k in fv.days[field].keys()])
    elif field.startswith('fk'):
        parts = field.split('_')
        dfd = pd.DataFrame(fv.days[parts[1]][parts[2]], columns=['date', parts[1]])
        dfd.plot(kind='bar', alpha=0.5, width=1, linewidth=.3, edgecolor='black')
        return create_select([f'fk_{parts[1]}_{k}' for k in fv.days[parts[1]].keys()]) +\
               get_chart_image_stream(field) + dfd.to_html(index=False)
    else:
        return ''


def get_viz_data(field):
    global fv
    if not fv.days:
        fv.get_days()
        print(f'Got {len(fv.days)} days')
    fv_keys = fv.get_cats()
    field_data = handle_on_select(field, fv)
    return field_data, fv_keys


@app.route('/')
def index():
    chart_select = create_select(range(20))
    return render_template('index.html', chart_select=chart_select)


@app.route('/<field>')
def pick_chart(field):
    chart_select = create_select(range(20))
    img_source = create_img(field)
    zip_files = read_zip()
    css = insert_css()
    field_data, fv_keys = get_viz_data(field)
    return render_template('chart.html', chart_select=chart_select, img_source=img_source,
                           field_data=field_data, zip_files=zip_files, css=css, fv_keys=fv_keys)

