import colorsys
from threading import Thread, Event
from time import sleep


class LedStrip:
    def __init__(self, node):
        self.node = node
        self.rgb_colors = [0, 0, 0]
        self.update_event = Event()
        self.thread = Thread(target=self.thread_function)
        self.thread.start()

    def set_color_rgb(self, rgb_colors):
        self.rgb_colors = rgb_colors
        self.update_event.set()

    def set_color_hsl(self, hsl_colors):
        self.rgb_colors = LedStrip.convert_hsl_to_rgb(hsl_colors)
        self.update_event.set()

    def get_color_rgb_str(self):
        return LedStrip.color_array_to_str(self.rgb_colors)

    def get_color_hsl_str(self):
        return LedStrip.color_array_to_str(LedStrip.convert_rgb_to_hsl(self.rgb_colors))

    def thread_function(self):
        while True:
            self.update_event.wait()
            self.update_event.clear()
            self.node.ColorRgb = LedStrip.color_array_to_str(self.rgb_colors)
            sleep(0.010)

    @staticmethod
    def color_array_to_str(array):
        return '%d,%d,%d' % (array[0], array[1], array[2])

    @staticmethod
    def convert_rgb_to_hsl(rgb_colors):
        hls = colorsys.rgb_to_hls(rgb_colors[0] / 255, rgb_colors[1] / 255, rgb_colors[2] / 255)
        return [hls[0] * 100, hls[2] * 100, hls[1] * 100]

    @staticmethod
    def convert_hsl_to_rgb(hsl_colors):
        rgb = colorsys.hls_to_rgb(hsl_colors[0] / 100, hsl_colors[2] / 100, hsl_colors[1] / 100)
        return [rgb[0] * 255, rgb[1] * 255, rgb[2] * 255]
