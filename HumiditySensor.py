from datetime import timedelta

from LoggedSensor import LoggedSensor


class HumiditySensor(LoggedSensor):
    def __init__(self, node):
        super(HumiditySensor, self).__init__(holdoff_time=timedelta(seconds=10))

        node.Humidity.subscribe_to_changes(self.on_property_changed)

    def on_property_changed(self, name, value):
        self.humidity = float(value)
        self.add_measurement(self.humidity)
