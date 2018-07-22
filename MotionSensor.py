import logging
from datetime import datetime


class MotionSensor:
    def __init__(self, node):
        self.node = node
        self.node.PulseCount.subscribe_to_changes(self.on_pulse_count_changed)
        self.last_movement_time = datetime.now() # let's assume there is movement on startup to avoid checks later

    def on_pulse_count_changed(self, name, value):
        logging.debug('movement detected! (%s)' % value)
        self.last_movement_time = datetime.now()

    def get_time_since_last_movement(self):
        return datetime.now() - self.last_movement_time
