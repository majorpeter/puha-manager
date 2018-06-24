from enum import Enum


class LightControl:
    class Mode(Enum):
        Manual = 0
        Auto = 1

    def __init__(self, led_strip, light_sensor):
        self.led_strip = led_strip
        self.light_sensor = light_sensor

        self.light_sensor.add_listener(self.on_light_measurement_changed)

        self.hue = 0
        self.saturation = 0
        self.lightness = 0
        self.mode = LightControl.Mode.Manual
        self.target_illuminance = 5

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
