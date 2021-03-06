import json
import logging
import os
import tempfile

from flask import Flask, render_template, request, Response, url_for
from flask.json import jsonify
from werkzeug.utils import redirect

from Database import Database
from LightControl import LightControl
from Slave import Slave

app = Flask(__name__)
with open('config.json') as config_file:
    config = json.load(config_file)

log_path = config['log_file_path'] if 'log_file_path' in config else tempfile.gettempdir() + os.path.sep + 'puha-manager.log'
logging.basicConfig(filename=log_path, format='%(asctime)s %(message)s', level=logging.DEBUG)

db_path = config['db_file_path'] if 'db_file_path' in config else tempfile.gettempdir() + os.path.sep + 'puha-manager-data.db'
Database(db_path)

slaves = []
slave_names = []
for slave_params in config['slaves']:
    slaves.append(Slave(slave_params['ip'], slave_params['port'], slave_params['name'], config))
    slave_names.append(slave_params['name'])

selected_slave_index = 0
slave = slaves[selected_slave_index]

header_data = {
    'site_title': config['site_title'],
    'navigation': [{
        'url': '/',
        'name': 'LED Control'
    }, {
        'url': '/temperature',
        'name': 'Temperature'
    }, {
        'url': '/humidity',
        'name': 'Humidity'
    }, {
        'url': '/illuminance',
        'name': 'Illuminance'
    }, {
        'url': '/settings',
        'name': 'Settings'
    }],
    'slaves': slave_names,
    'slave_index': selected_slave_index,
}


def update_header_data(request):
    header_data['request_path'] = request.path


@app.route('/')
def index():
    data = []
    if slave.motion_sensor is not None:
        time_delta = slave.motion_sensor.get_time_since_last_movement()
        data.append(('Last movement', '%d sec ago' % time_delta.seconds))

    update_header_data(request)
    animations = None
    if slave.light_control is not None:
        animations = []
        for item in slave.light_control.animation_collection:
            animations.append(item['name'])
    return render_template('index.html', **header_data, data=data, light_control=slave.light_control is not None, animations=animations)


@app.route('/led', methods=['GET', 'POST'])
def ledstrip_control():
    if request.method == 'POST':
        if 'rgb' in request.form:
            rgb_colors = list(map(int, request.form['rgb'].split(',')))
            if 'animate' not in request.form:
                if slave.light_control is not None:
                    slave.light_control.mode = LightControl.Mode.Manual
                slave.ledstrip.set_color_rgb(rgb_colors)
            else:
                if slave.light_control is not None:
                    slave.light_control.mode = LightControl.Mode.Manual
                slave.ledstrip.animate_to_rgb(rgb_colors, float(request.form['animate']))
        elif 'hsl' in request.form:
            hsl_colors = list(map(int, request.form['hsl'].split(',')))
            if slave.light_control is not None:
                slave.light_control.mode = LightControl.Mode.Manual
            slave.ledstrip.set_color_hsl(hsl_colors)
        return ''
    elif request.method == 'GET':
        return jsonify({
            'rgb': slave.ledstrip.get_color_rgb_str(),
            'hsl': slave.ledstrip.get_color_hsl_str()
        })


@app.route('/lightcontrol', methods=['GET', 'POST'])
def light_control():
    if request.method == 'POST':
        illuminance = None
        if 'illuminance' in request.form:
            illuminance = float(request.form['illuminance'])
        slave.light_control.set_mode(mode=LightControl.Mode[request.form['mode']],
                             illuminance=illuminance,
                             animation_index=int(request.form['anim_index']) if 'anim_index' in request.form else None)
        return ''
    elif request.method == 'GET':
        return jsonify({
            'mode': str(slave.light_control.mode),
            'anim_index': slave.light_control.animation_index
        })


@app.route('/lightsensor', methods=['GET'])
def light_sensor():
    return jsonify({
        'illuminance': slave.light_sensor.illuminance
    })


def chart(sensor, title=None, y_label=None, suggested_min=None, suggested_max=None, dataset_color=None):
    last_timestamp = 0
    if request.method == 'POST' and 'last_timestamp' in request.form:
        last_timestamp = int(request.form['last_timestamp'])
    label, data, last_timestamp = sensor.get_chart_data(from_timestamp=last_timestamp + 1)

    if request.method == 'GET':
        update_header_data(request)
        return render_template('chart.html',
                **header_data,
                chart_title=title,
                y_scale_label=y_label,
                suggested_min=suggested_min,
                suggested_max=suggested_max,
                dataset_color='rgba({0},{1},{2},0.5)'.format(*dataset_color),
                dataset_border_color='rgb({0},{1},{2})'.format(*dataset_color),
                refresh_period_ms=int(sensor.holdoff_time.total_seconds() / 2 * 1000),
                chart_width='700px',
                chart_labels_json=('["' + ('","'.join(label)) + '"]'),
                chart_data_json=('[' + (','.join(data)) + ']'),
                chart_last_timestamp=last_timestamp)
    if request.method == 'POST':
        return jsonify({
            'label': label,
            'data': data,
            'last_timestamp': last_timestamp
        })


@app.route('/illuminance', methods=['GET', 'POST'])
def illuminance_chart():
    return chart(slave.light_sensor,
                 title='Illuminance',
                 y_label='Illuminance (lx)',
                 suggested_min=0,
                 dataset_color=[238, 229, 25])


@app.route('/temperature', methods=['GET', 'POST'])
def temperature_chart():
    return chart(slave.temperature_sensor,
                 title='Temperature',
                 y_label='Temperature (C)',
                 suggested_min=20,
                 suggested_max=30,
                 dataset_color=[224, 120, 23])


@app.route('/humidity', methods=['GET', 'POST'])
def humidity_chart():
    return chart(slave.humidity_sensor,
                 title='Relative Humidity',
                 y_label='R/H (%)',
                 suggested_min=0,
                 suggested_max=100,
                 dataset_color=[75, 192, 192])


@app.route('/settings', methods=['GET', 'POST'])
def settings_page():
    setting_error = None
    if request.method == 'POST':
        if 'apply' in request.form:
            try:
                config['site_title'] = request.form['site_title']
                header_data['site_title'] = config['site_title']

                config['motion_timeout_sec'] = float(request.form['motion_timeout_sec'])
                config['target_nighttime_illuminance'] = float(request.form['target_nighttime_illuminance'])
                config['light_sensor_quantization_error'] = float(request.form['light_sensor_quantization_error'])
                config['light_control_k_p'] = float(request.form['light_control_k_p'])
                config['light_control_k_i'] = float(request.form['light_control_k_i'])
            except ValueError as error:
                setting_error = str(error)
        elif 'save' in request.form:
            with open('config.json', 'w') as config_file:
                json.dump(config, config_file, indent=4)

    update_header_data(request)
    return render_template('settings.html', **header_data, config=config, setting_error=setting_error)


@app.route('/selectslave/<int:index>')
def select_slave(index):
    global selected_slave_index, slave, slaves, header_data

    selected_slave_index = index
    slave = slaves[selected_slave_index]
    header_data['slave_index'] = selected_slave_index

    return redirect(url_for('index'))

@app.route('/log')
def log_view():
    with open(log_path, 'r') as log_file:
        return Response(log_file.read(), mimetype='text/plain')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
