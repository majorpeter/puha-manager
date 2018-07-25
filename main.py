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


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
