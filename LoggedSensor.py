from datetime import datetime
from threading import Lock

from Database import Database


class LoggedSensor:
    """
    This is a common base class for all sensors that have data to be stored/logged.
    """

    registered_type_ids = []

    def __init__(self, type_id, max_measurements=200, holdoff_time=None):
        if type_id is LoggedSensor.registered_type_ids:
            raise BaseException('Type ID already exists: %d' % type_id)

        self.type_id = type_id
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
            Database.instance.insert_measurement(now.timestamp(), self.type_id, measurement)

    def get_chart_data(self, from_timestamp=0):
        label = []
        data = []
        last_timestamp = 0

        with self.lock:
            for item in self.data:
                if item['time'].timestamp() > from_timestamp:
                    label.append(item['time'].strftime('%H:%M:%S'))
                    data.append('%.2f' % item['measurement'])

            if len(self.data) > 0:
                last_timestamp = int(self.data[-1]['time'].timestamp())

        return label, data, last_timestamp
