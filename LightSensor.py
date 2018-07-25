class LightSensor:
    def __init__(self, node):
        self.node = node
        self.illuminance = 0
        self.listeners = []

        self.node.Illuminance.subscribe_to_changes(self.on_property_changed)

    def add_listener(self, listener):
        """
        add callback function to call when measurement is updated
        :param listener: callback function that takes single argument (float: measurement in Lx)
        """
        self.listeners.append(listener)

    def on_property_changed(self, name, value):
        self.illuminance = float(value)
        for listener in self.listeners:
            listener(self.illuminance)
