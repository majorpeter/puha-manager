import colorsys

from flask import Flask, render_template, request
from flask.json import jsonify

from Slave import Slave

app = Flask(__name__)
slave = Slave('192.168.0.211', 23)
rgb_colors = [0, 0, 0]


@app.route('/')
def index():
    data = []
    data.append(('Temperature', slave.get_temperature()))
    data.append(('RH', slave.get_humidity_percentage()))
    data.append(('Light', slave.get_light_lux()))

    return render_template('index.html', data=data)


@app.route('/led', methods=['GET', 'POST'])
def ledstrip_control():
    global rgb_colors

    if request.method == 'POST':
        rgb_str = request.form['rgb']
        rgb_colors = list(map(int, rgb_str.split(',')))
        slave.client.root.LEDSTRIP.ColorRgb = rgb_str
        return ''
    elif request.method == 'GET':
        return jsonify({
            'rgb': color_array_to_str(rgb_colors),
            'hsl': color_array_to_str(get_hsl_colors(rgb_colors))
        })


def color_array_to_str(array):
    return '%d,%d,%d' % (array[0], array[1], array[2])


def get_hsl_colors(rgb_colors):
    hls = colorsys.rgb_to_hls(rgb_colors[0] / 255, rgb_colors[1] / 255, rgb_colors[2] / 255)
    return [hls[0] * 100, hls[2] * 100, hls[1] * 100]


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
