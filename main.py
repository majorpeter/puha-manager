from flask import Flask

from Slave import Slave

app = Flask(__name__)
slave = Slave('192.168.0.211', 23)


@app.route('/')
def index():
    data = []
    data.append(('Temperature', slave.get_temperature()))
    data.append(('RH', slave.get_humidity_percentage()))
    data.append(('Light', slave.get_light_lux()))
    return '<html><head><script type="text/javascript">setTimeout(function(){location.reload();}, 1000);</script></head><body>' + str(data) + '</body></html>'


if __name__ == '__main__':
    app.run(debug=True)
