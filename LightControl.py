from datetime import timedelta
from enum import Enum


class LightControl:
    class Mode(Enum):
        Manual = 0
        Auto = 1

    TARGET_ILLUMINANCE_NIGHTTIME = 3

    def __init__(self, led_strip, light_sensor, motion_sensor):
        self.led_strip = led_strip
        self.light_sensor = light_sensor
        self.motion_sensor = motion_sensor

        self.light_sensor.add_listener(self.on_light_measurement_changed)

        self.hue = 0
        self.saturation = 0
        self.lightness = 0
        self.mode = LightControl.Mode.Manual
        self.target_illuminance = LightControl.TARGET_ILLUMINANCE_NIGHTTIME

    def set_mode(self, mode):
        if mode == LightControl.Mode.Auto:
            hsl = self.led_strip.get_color_hsl()
            self.hue = hsl[0]
            self.saturation = hsl[1]
            self.lightness = hsl[2]
        self.mode = mode

    def on_light_measurement_changed(self, measurement):
        if self.mode == LightControl.Mode.Manual:
            return

        if self.motion_sensor.get_time_since_last_movement() > timedelta(seconds=60):
            self.target_illuminance = 0
        else:
            self.target_illuminance = LightControl.TARGET_ILLUMINANCE_NIGHTTIME

        error = self.target_illuminance - measurement
        self.lightness += error * 0.8
        if self.lightness < 0:
            self.lightness = 0
        elif self.lightness > 100:
            self.lightness = 100

        self.led_strip.set_color_hsl([
            self.hue,
            self.saturation,
            self.lightness
        ])
