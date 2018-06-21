from LedStrip import LedStrip
from LightControl import LightControl
from LightSensor import LightSensor
from mprotocol_client_python.Client import Client


class Slave:
    def __init__(self, ip_address, port):
        self.client = Client(ip_address, port, timeout=1)

        self.ledstrip = None
        self.light_sensor = None
        for node in self.client.root.get_children():
            if node.get_name() == 'LEDSTRIP':
                self.ledstrip = LedStrip(node)
            elif node.get_name() == 'HTU':
                self.htu_sensor = self.client.root.HTU
            elif node.get_name() == 'LIGHT':
                self.light_sensor = LightSensor(self.client.root.LIGHT)

        if self.ledstrip and self.light_sensor:
            self.light_control = LightControl(self.ledstrip, self.light_sensor)

    def get_temperature(self):
        return float(str(self.htu_sensor.Temperature))

    def get_humidity_percentage(self):
        return float(str(self.htu_sensor.Humidity))

    def get_light_lux(self):
        return float(self.light_sensor.illuminance)
