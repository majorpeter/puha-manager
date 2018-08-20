from datetime import timedelta

from LoggedSensor import LoggedSensor


class HumiditySensor(LoggedSensor):
    def __init__(self, node):
        super(HumiditySensor, self).__init__(type_id=2, max_measurements=500, holdoff_time=timedelta(minutes=1))

        node.Humidity.subscribe_to_changes(self.on_property_changed)

    def on_property_changed(self, name, value):
        self.humidity = float(value)
        self.add_measurement(self.humidity)
