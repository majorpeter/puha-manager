import json
import logging

from flask import Flask, render_template, request
from flask.json import jsonify

from LightControl import LightControl
from Slave import Slave

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
app = Flask(__name__)
with open('config.json') as config_file:
    config = json.load(config_file)

slave_params = config['slaves'][0] #TODO support more slaves!
slave = Slave(slave_params['ip'], slave_params['port'], config)

@app.route('/')
def index():
    data = []
    data.append(('Temperature', slave.get_temperature()))
    data.append(('RH', slave.get_humidity_percentage()))
    data.append(('Light', slave.get_light_lux()))
    time_delta = slave.motion_sensor.get_time_since_last_movement()
    data.append(('Last movement', '%d sec ago' % time_delta.seconds))

    return render_template('index.html', data=data)


@app.route('/led', methods=['GET', 'POST'])
def ledstrip_control():
    if request.method == 'POST':
        if 'rgb' in request.form:
            rgb_colors = list(map(int, request.form['rgb'].split(',')))
            if 'animate' not in request.form:
                slave.light_control.mode = LightControl.Mode.Manual
                slave.ledstrip.set_color_rgb(rgb_colors)
            else:
                slave.light_control.mode = LightControl.Mode.Manual
                slave.ledstrip.animate_to_rgb(rgb_colors, float(request.form['animate']))
        elif 'hsl' in request.form:
            hsl_colors = list(map(int, request.form['hsl'].split(',')))
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
        slave.light_control.set_mode(LightControl.Mode[request.form['mode']], illuminance)
        return ''
    elif request.method == 'GET':
        return jsonify({
            'mode': str(slave.light_control.mode)
        })


@app.route('/lightsensor', methods=['GET'])
def light_sensor():
    return jsonify({
        'illuminance': slave.light_sensor.illuminance
    })


@app.route('/chart', methods=['GET', 'POST'])
def chart():
    last_timestamp = 0
    if request.method == 'POST' and 'last_timestamp' in request.form:
        last_timestamp = int(request.form['last_timestamp'])
    label, data, last_timestamp = slave.light_sensor.get_chart_data(from_timestamp=last_timestamp + 1)

    if request.method == 'GET':
        return render_template('chart.html',
                y_scale_label='Illuminance (lx)',
                refresh_period_ms=int(slave.light_sensor.holdoff_time.total_seconds() / 2 * 1000),
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


@app.route('/settings', methods=['GET', 'POST'])
def settings_page():
    setting_error = None
    if request.method == 'POST':
        if 'apply' in request.form:
            try:
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

    return render_template('settings.html', config=config, setting_error=setting_error)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
