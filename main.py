from flask import Flask, render_template, request
from flask.json import jsonify

from LightControl import LightControl
from Slave import Slave

app = Flask(__name__)
slave = Slave('192.168.0.211', 23)


@app.route('/')
def index():
    data = []
    data.append(('Temperature', slave.get_temperature()))
    data.append(('RH', slave.get_humidity_percentage()))
    data.append(('Light', slave.get_light_lux()))

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
        if request.form['auto'] == 'true':
            slave.light_control.set_mode(LightControl.Mode.Auto)
        elif request.form['auto'] == 'false':
            slave.light_control.set_mode(LightControl.Mode.Manual)
        return ''
    elif request.method == 'GET':
        return jsonify({
            'auto': slave.light_control.mode == LightControl.Mode.Auto
        })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
