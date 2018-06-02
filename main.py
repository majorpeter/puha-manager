from flask import Flask, render_template

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


if __name__ == '__main__':
    app.run(debug=True)
