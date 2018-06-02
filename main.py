from flask import Flask

from Slave import Slave

app = Flask(__name__)
slave = Slave('192.168.0.211', 23)


@app.route('/')
def index():
    output = 'Temp: %.1f °C<br/>\n' % slave.get_temperature()
    output += 'RH: %d %%\n<br/>' % slave.get_humidity_percentage()
    return output
