import colorsys
from datetime import time, datetime, timedelta
from threading import Thread, Event
from time import sleep


class LedStrip:
    def __init__(self, node):
        self.node = node
        self.rgb_colors = [0, 0, 0]
        self.animation_from = None
        self.animation_to = None
        self.animation_start = None
        self.animation_end = None

        self.update_event = Event()
        self.thread = Thread(target=self.thread_function)
        self.thread.start()

    def clear_animation(self):
        self.animation_from = None
        self.animation_to = None
        self.animation_start = None
        self.animation_end = None

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

        self.animation_start = datetime.now()
        self.animation_end = self.animation_start + timedelta(seconds=duration_sec)
        self.animation_from = self.rgb_colors[:]
        self.animation_to = rgb_color

        self.update_event.set()

    def get_color_rgb_str(self):
        return LedStrip.color_array_to_str(self.rgb_colors)

    def get_color_hsl_str(self):
        return LedStrip.color_array_to_str(LedStrip.convert_rgb_to_hsl(self.rgb_colors))

    def thread_function(self):
        while True:
            self.update_event.wait()

            if self.animation_to:
                duration = self.animation_end - self.animation_start
                elapsed = datetime.now() - self.animation_start
                state = elapsed / duration
                if state < 1:
                    self.rgb_colors = [
                        int(self.animation_from[0] * (1 - state) + self.animation_to[0] * state),
                        int(self.animation_from[1] * (1 - state) + self.animation_to[1] * state),
                        int(self.animation_from[2] * (1 - state) + self.animation_to[2] * state)
                    ]
                else:
                    self.rgb_colors = self.animation_to
                    self.clear_animation()
                    self.update_event.clear()
            else:
                self.update_event.clear()
            self.node.ColorRgb = LedStrip.color_array_to_str(self.rgb_colors)
            sleep(0.010)

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
