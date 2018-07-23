from datetime import timedelta
from enum import Enum


class LightControl:
    class Mode(Enum):
        Manual = 0
        Auto = 1

    def __init__(self, config, led_strip, light_sensor, motion_sensor):
        self.config = config
        self.led_strip = led_strip
        self.light_sensor = light_sensor
        self.motion_sensor = motion_sensor

        self.light_sensor.add_listener(self.on_light_measurement_changed)

        self.hue = 0
        self.saturation = 0
        self.integrator = 0
        self.mode = LightControl.Mode.Manual

    def set_mode(self, mode):
        if mode == LightControl.Mode.Auto:
            hsl = self.led_strip.get_color_hsl()
            self.hue = hsl[0]
            self.saturation = hsl[1]
            self.integrator = hsl[2]
        self.mode = mode

    def on_light_measurement_changed(self, measurement):
        """
        updates light control according to configuration
        :param measurement: light measurement value (in lx)
        Integrator anti-windup solution based on http://cse.lab.imtlucca.it/~bemporad/teaching/ac/pdf/AC2-09-AntiWindup.pdf
          e -> error
          K_p -> 'light_control_k_p'
          K_p/T_i -> 'light_control_k_i'
          1/T_t -> 'light_control_anti_windup_time'
        """
        if self.mode == LightControl.Mode.Manual:
            return

        if self.motion_sensor.get_time_since_last_movement() > timedelta(seconds=self.config['motion_timeout_sec']):
            target_illuminance = 0
        else:
            target_illuminance = self.config['target_nighttime_illuminance']

        error = target_illuminance - measurement
        # since the measurement is quantized, the error can never reach zero
        if abs(error) < self.config['light_sensor_quantization_error']:
            error = 0

        # update integrator
        self.integrator += error * self.config['light_control_k_i']

        # output value (v)
        lightness = self.config['light_control_k_p'] * error + self.integrator

        # saturate output signal (u) into the range of lightness (0-100); handle integrator wind-up
        if lightness < 0:
            self.integrator += self.config['light_control_anti_windup_time'] * (0 - lightness)
            lightness = 0
        elif lightness > 100:
            self.integrator += self.config['light_control_anti_windup_time'] * (100 - lightness)
            lightness = 100

        self.led_strip.set_color_hsl([
            self.hue,
            self.saturation,
            lightness
        ])
