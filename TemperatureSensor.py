from datetime import timedelta

from LoggedSensor import LoggedSensor


class TemperatureSensor(LoggedSensor):
    def __init__(self, node):
        super(TemperatureSensor, self).__init__(holdoff_time=timedelta(seconds=10))

        node.Temperature.subscribe_to_changes(self.on_property_changed)

    def on_property_changed(self, name, value):
        self.temperature = float(value)
        self.add_measurement(self.temperature)
