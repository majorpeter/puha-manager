from LedStrip import LedStrip
from mprotocol_client_python.Client import Client


class Slave:
    def __init__(self, ip_address, port):
        self.client = Client(ip_address, port, timeout=1)

        for node in self.client.root.get_children():
            if node.get_name() == 'LEDSTRIP':
                self.ledstrip = LedStrip(node)
            elif node.get_name() == 'HTU':
                self.htu_sensor = self.client.root.HTU
            elif node.get_name() == 'LIGHT':
                self.light_sensor = self.client.root.LIGHT

    def get_temperature(self):
        return float(str(self.htu_sensor.Temperature))

    def get_humidity_percentage(self):
        return float(str(self.htu_sensor.Humidity))

    def get_light_lux(self):
        return float(str(self.light_sensor.Illuminance))
