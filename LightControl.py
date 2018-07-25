from datetime import timedelta
from enum import Enum
from threading import Thread
from time import sleep


class LightControl:
    class Mode(Enum):
        Manual = 0
        NightTime = 1
        KeepIlluminance = 2

    CONTROL_LOOP_FREQUENCY_HZ = 30

    def __init__(self, config, led_strip, light_sensor, motion_sensor):
        self.config = config
        self.led_strip = led_strip
        self.light_sensor = light_sensor
        self.motion_sensor = motion_sensor

        self.hue = 0
        self.saturation = 0
        self.initial_illuminance = 0
        self.integrator = 0
        self.mode = LightControl.Mode.Manual

        self.control_loop_thread = Thread(target=self.control_loop_thread_func)
        self.control_loop_thread.start()

    def set_mode(self, mode):
        if mode in [LightControl.Mode.NightTime, LightControl.Mode.KeepIlluminance]:
            hsl = self.led_strip.get_color_hsl()
            self.hue = hsl[0]
            self.saturation = hsl[1]
            self.integrator = hsl[2] #TODO calculate actual value
        self.mode = mode
        self.initial_illuminance = self.light_sensor.illuminance

    def control_loop_thread_func(self):
        """
        updates light control according to configuration
        Integrator anti-windup solution based on http://cse.lab.imtlucca.it/~bemporad/teaching/ac/pdf/AC2-09-AntiWindup.pdf
          e -> error
          K_p -> 'light_control_k_p'
          K_p/T_i -> 'light_control_k_i'
          1/T_t -> 'light_control_anti_windup_time'
        """
        while True:
            if self.mode == LightControl.Mode.Manual:
                # no need for control
                sleep(1) #TODO event instead?
                continue
            elif self.mode == LightControl.Mode.NightTime:
                if self.motion_sensor.get_time_since_last_movement() > timedelta(seconds=self.config['motion_timeout_sec']):
                    target_illuminance = 0
                else:
                    target_illuminance = self.config['target_nighttime_illuminance']
            else: # KeepIlluminance
                target_illuminance = self.initial_illuminance

            error = target_illuminance - self.light_sensor.illuminance
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

            sleep(1 / LightControl.CONTROL_LOOP_FREQUENCY_HZ)
