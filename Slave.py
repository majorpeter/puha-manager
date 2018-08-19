from LedStrip import LedStrip
from LightControl import LightControl
from LightSensor import LightSensor
from MotionSensor import MotionSensor
from TemperatureSensor import TemperatureSensor
from mprotocol_client_python.Client import Client


class Slave:
    def __init__(self, ip_address, port, config):
        self.client = Client(ip_address, port, timeout=1)

        self.ledstrip = None
        self.light_sensor = None
        for node in self.client.root.get_children():
            if node.get_name() == 'LEDSTRIP':
                self.ledstrip = LedStrip(node)
            elif node.get_name() == 'HTU':
                self.temperature_sensor = TemperatureSensor(node)
            elif node.get_name() == 'LIGHT':
                self.light_sensor = LightSensor(self.client.root.LIGHT)
            elif node.get_name() == 'MOTION':
                self.motion_sensor = MotionSensor(self.client.root.MOTION)

        if self.ledstrip and self.light_sensor and self.motion_sensor:
            self.light_control = LightControl(config, self.ledstrip, self.light_sensor, self.motion_sensor)

    def get_humidity_percentage(self):
        return float(str(self.htu_sensor.Humidity))

    def get_light_lux(self):
        return float(self.light_sensor.illuminance)
