import colorsys
import logging
from threading import Thread, Event
from time import sleep

from Animation import LinearInterpolateAnimation


class LedStrip:
    LED_COUNT = 180

    def __init__(self, node):
        self.node = node
        self.rgb_colors = [0, 0, 0]
        self.animation = None
        self.color_bytes_str = ''

        self.update_event = Event()

        self.thread = Thread(target=self.thread_function)
        self.thread.start()

    def clear_animation(self):
        self.animation = None
        self.update_event.set()

    def set_color_rgb(self, rgb_colors):
        self.clear_animation()
        self.rgb_colors = rgb_colors
        self.update_event.set()

    def set_color_hsl(self, hsl_colors):
        self.clear_animation()
        self.rgb_colors = LedStrip.convert_hsl_to_rgb(hsl_colors)
        self.update_event.set()

    def animate_to_rgb(self, rgb_color, duration_sec):
        self.clear_animation()
        self.animation = LinearInterpolateAnimation(LedStrip.LED_COUNT, self.rgb_colors, rgb_color, duration_sec)
        self.rgb_colors = rgb_color[:]
        self.update_event.set()

    def get_color_rgb_str(self):
        return LedStrip.color_array_to_str(self.rgb_colors)

    def get_color_hsl(self):
        return LedStrip.convert_rgb_to_hsl(self.rgb_colors)

    def get_color_hsl_str(self):
        return LedStrip.color_array_to_str(LedStrip.convert_rgb_to_hsl(self.rgb_colors))

    def thread_function(self):
        while True:
            self.update_event.wait()
            write_current_color_and_clear_evt = True
            if self.animation:
                anim_result = self.animation.step()
                if anim_result:
                    value_str = ''
                    for color in anim_result:
                        value_str += '%02x%02x%02x' % (color[0], color[1], color[2])
                    self.update_color_bytes(value_str)
                    write_current_color_and_clear_evt = False

            if write_current_color_and_clear_evt:
                self.update_color_bytes(('%02x%02x%02x' % (self.rgb_colors[0], self.rgb_colors[1], self.rgb_colors[2])) * LedStrip.LED_COUNT)
                self.update_event.clear()
            sleep(0.010)

    def update_color_bytes(self, color_bytes_str):
        """
        update LED colors on device (if required)
        :param color_bytes_str: HEX string containing the color of each LED
        """
        if self.color_bytes_str == color_bytes_str:
            return # no need to update
        try:
            self.node.ColorBytes = color_bytes_str
            self.color_bytes_str = color_bytes_str
        except BaseException:
            logging.error('Writing LED strip failed')

    @staticmethod
    def color_array_to_str(array):
        return '%d,%d,%d' % (array[0], array[1], array[2])

    @staticmethod
    def convert_rgb_to_hsl(rgb_colors):
        hls = colorsys.rgb_to_hls(rgb_colors[0] / 255, rgb_colors[1] / 255, rgb_colors[2] / 255)
        return [int(hls[0] * 100), int(hls[2] * 100), int(hls[1] * 100)]

    @staticmethod
    def convert_hsl_to_rgb(hsl_colors):
        rgb = colorsys.hls_to_rgb(hsl_colors[0] / 100, hsl_colors[2] / 100, hsl_colors[1] / 100)
        return [int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255)]
