# flask-forecast-viewer
___
Flask-forecast-viewer is a Flask-server that scrapes data from [buienradar.nl](buienradar.nl), creates visualizations using Matplotlib and puts it in a dynamic website using Flask. We're planning on hosting the first working version of the server on [weather.taekeroukema.xyz](https://taekeroukema.xyz)

## How to install
At the moment the scripts only scrape [buienradar.nl](buienradar.nl) and create a .png file with the visualization so it isn't worth it to install. But if you want to you can just `git clone https://github.com/Taektiek/flask-forecast-viewer.git` and use `python3` to run it. On my own server we run the scraping script every two ours. You can find that at [taekeroukema.xyz](taekeroukema.xyz/weather.zip).

## Planned features
* Request graph from website
* Automatically create visualizations
