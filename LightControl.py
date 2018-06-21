class LightControl:
    def __init__(self, led_strip, light_sensor):
        self.led_strip = led_strip
        self.light_sensor = light_sensor

        self.light_sensor.add_listener(self.on_light_measurement_changed)

        self.hsl_default = [40, 40, 0]
        self.lightness = 0
        self.target_illuminance = 15

    def on_light_measurement_changed(self, measurement):
        error = self.target_illuminance - measurement
        self.lightness += error * 0.8
        if self.lightness < 0:
            self.lightness = 0
        elif self.lightness > 100:
            self.lightness = 100

        self.led_strip.set_color_hsl([
            self.hsl_default[0],
            self.hsl_default[1],
            self.lightness
        ])
