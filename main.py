from flask import Flask, render_template, request

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


@app.route('/led', methods=['POST'])
def ledstrip_control():
    rgb_str = request.form['rgb']
    slave.client.root.LEDSTRIP.ColorRgb = rgb_str
    return ''


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
