from datetime import datetime
from threading import Lock


class LoggedSensor:
    """
    This is a common base class for all sensors that have data to be stored/logged.
    """

    def __init__(self, max_measurements=200, holdoff_time=None):
        self.data = []
        self.max_measurements = max_measurements
        self.holdoff_time = holdoff_time
        self.lock = Lock()

    def add_measurement(self, measurement):
        now = datetime.now()

        with self.lock:
            if self.holdoff_time is not None:
                if len(self.data) > 0:
                    diff = now - self.data[-1]['time']
                    if diff < self.holdoff_time:
                        return

            if len(self.data) > self.max_measurements:
                del self.data[0]

            self.data.append({'time': now, 'measurement': measurement})

    def get_chart_data(self):
        label = []
        data = []

        with self.lock:
            for item in self.data:
                label.append('\'' + item['time'].strftime('%H:%M:%S') + '\'')
                data.append('%.2f' % item['measurement'])
            last_timestamp = int(self.data[-1]['time'].timestamp())

        return label, data, last_timestamp
