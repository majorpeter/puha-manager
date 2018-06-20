from datetime import datetime, timedelta


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
