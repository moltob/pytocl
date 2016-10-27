from pytocl.car import State


class Plan:
    def __init__(self, strategy):
        self.strategy = strategy
        self.state = None

        self.speed_setting = {
            0: 80,
            150: 20,
            240: 80,
            370: 15,
            540: 80,
            690: 20,
            800: 80,
            950: 15,
            1000: 80,
            1430: 20,
            1500: 80,
            1850: 20,
            1960: 80,
            2300: 20,
            2400: 8,
            2580: 80,
            2660: 20,
            2760: 80,
            2900: 15,
            2950: 80,
            3200: 10,
            3320: 80
        }

    def get_desired_position(self):
        return 0

    def get_desired_speed(self):
        index = max([x for x in self.speed_setting.keys() if x < self.state.distance_from_start])
        return self.speed_setting[index]

    def get_desired_angle(self):
        return 0

    def get_desired_focus(self):
        return 0