import os
import zipfile
import shutil

import requests
from datetime import datetime as dt

class ForecastSnapper():

    def __init__(self):
        self.url = 'https://forecast.buienradar.nl/2.0/forecast/2759794'
        self.request_header = headers = {'User-Agent': u'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36            (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36', 'X-Cookies-Accepted': '1'}
        ts = dt.now().strftime('%Y%m%d%H%M')
        self.file_name = fr'/var/www/taekeroukema.xyz/html/weather/forecasts_{ts}.json'
        self.permanent_file_name = fr'/var/www/taekeroukema.xyz/html/weather/forecasts.json'
        self.zip_file = fr'/var/www/taekeroukema.xyz/html/weather/forecasts.zip'

    def snap_and_store_forecast(self):
        r = requests.get(self.url, headers=self.request_header)
        with open(self.file_name, 'w') as f:
            f.write(r.text)
        shutil.copy2(self.file_name,self.permanent_file_name)
        self.archive_snap(self.file_name)

    def archive_snap(self, source_path):
        with zipfile.ZipFile(self.zip_file, 'a', compression=zipfile.ZIP_DEFLATED) as zipf:
            # Add a file located at the source_path to the destination within the zip
            # file. It will overwrite existing files if the names collide, but it
            # will give a warning
            zipf.write(source_path, os.path.basename(source_path))

ForecastSnapper().snap_and_store_forecast()
