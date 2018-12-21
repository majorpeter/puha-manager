from datetime import datetime, timedelta
from random import randint


class Animation:
    def __init__(self, led_count):
        self.led_count = led_count

    def step(self): raise NotImplementedError
    """
    :return LED color values as binary string
            None if done
    """


class LinearInterpolateAnimation(Animation):
    def __init__(self, led_count, rgb_from, rgb_to, duration_sec):
        super(LinearInterpolateAnimation, self).__init__(led_count)

        self.animation_start = datetime.now()
        self.animation_end = self.animation_start + timedelta(seconds=duration_sec)
        self.animation_from = rgb_from
        self.animation_to = rgb_to

    def step(self):
        duration = self.animation_end - self.animation_start
        elapsed = datetime.now() - self.animation_start
        state = elapsed / duration
        if state < 1:
            color = [
                int(self.animation_from[0] * (1 - state) + self.animation_to[0] * state),
                int(self.animation_from[1] * (1 - state) + self.animation_to[1] * state),
                int(self.animation_from[2] * (1 - state) + self.animation_to[2] * state)
            ]
            return [color] * self.led_count
        else:
            return None


class KnightRiderAnimation(Animation):
    def __init__(self, led_count, active_led_count, color, length, speed):
        """
        :param color: color of moving line
        :param length: length of moving line (LED count)
        :param speed: speed of movement in [LED/s]
        """
        super(KnightRiderAnimation, self).__init__(led_count)
        self.active_led_count = active_led_count
        self.color = color
        self.length = length
        self.speed = speed

        self.position = 0
        self.direction = 1
        self.last_movement_time = datetime.now()

    def step(self):
        now = datetime.now()
        delta_time = now - self.last_movement_time
        delta_led = int(self.speed * (delta_time / timedelta(seconds=1)))
        if delta_led > 0:
            self.last_movement_time = now
            self.position += self.direction * delta_led
            if self.position >= self.active_led_count - self.length:
                self.position = self.active_led_count - self.length
                self.direction = -1
            elif self.position <= 0:
                self.position = 0
                self.direction = 1
        result = [[0, 0, 0]] * self.led_count
        for i in range(self.position, self.position + self.length):
            result[i] = self.color[:]
        return result


class XmasAnimation(Animation):
    COLORS = [
        [95, 0, 0], # red
        [0, 75, 0], # green
        [0, 0, 80], # blue
        [60, 20, 0], # yellow
    ]

    SPEED = 0.02

    def __init__(self, led_count, randomize_channel):
        super(XmasAnimation, self).__init__(led_count)
        self.randomize_channel = randomize_channel
        self.last_time = datetime.now()
        self.brightnesses = [0, 0, 0, 0]
        self.channel_index = 0
        self.direction = 1

    def step(self):
        pattern_length = len(self.brightnesses)

        now = datetime.now()
        delta_time = now - self.last_time
        self.last_time = now

        self.brightnesses[self.channel_index] += self.direction * XmasAnimation.SPEED
        if self.brightnesses[self.channel_index] > 1:
            self.brightnesses[self.channel_index] = 1
            self.direction = -1
        elif self.brightnesses[self.channel_index] < 0:
            self.brightnesses[self.channel_index] = 0
            self.direction = 1

            if self.randomize_channel:
                self.channel_index = (self.channel_index + randint(1, pattern_length - 1)) % pattern_length
            else:
                # simply next channel with wrapping
                self.channel_index = (self.channel_index + 1) % pattern_length

        result = [[0, 0, 0]] * self.led_count
        for i in range(int(self.led_count / pattern_length)):
            for j in range(pattern_length):
                result[i* pattern_length + j] = [int(k * self.brightnesses[j]) for k in XmasAnimation.COLORS[j]]

        return result
