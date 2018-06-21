from threading import Thread
from time import sleep


class LightSensor:
    def __init__(self, node):
        self.node = node
        self.illuminance = 0
        self.listeners = []

        self.thread = Thread(target=self.thread_function)
        self.thread.start()

    def add_listener(self, listener):
        """
        add callback function to call when measurement is updated
        :param listener: callback function that takes single argument (float: measurement in Lx)
        """
        self.listeners.append(listener)

    def thread_function(self):
        while True:
            try:
                self.illuminance = float(str(self.node.Illuminance))
                for listener in self.listeners:
                    listener(self.illuminance)
            except BaseException:
                print('Error while reading light sensor')
            sleep(0.1)
