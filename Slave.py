from mprotocol_client_python.Client import Client


class Slave:
    def __init__(self, ip_address, port):
        self.client = Client(ip_address, port)
        self.htu_sensor = self.client.root.HTU

    def get_temperature(self):
        return float(str(self.htu_sensor.Temperature))

    def get_humidity_percentage(self):
        return float(str(self.htu_sensor.Humidity))
