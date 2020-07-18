from flask import Flask, render_template

app = Flask(__name__)

def create_select(options, selected=0):
    action = 'window.location.href="this.value"'
    options = '\n'.join([f'<option value={v}>v</>' for v in options])
    return f'<select name="colour" method="GET" action="/" onchange=\'{action}\'>{options}</select>'


@app.route('/')
def index():
    chart_select = create_select(range(20))
    return render_template('index.html', chart_select=chart_select)

@app.route('/<field>')
def pick_chart(field):
    return f'Soon here you will see {field}.png.'

