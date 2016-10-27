from pytocl.car import State
import math

from shockwave.pid import PID


class Plan:
    def __init__(self, strategy):
        self.strategy = strategy
        self.state = None
        self.pid = PID(1, 30, 0)


    def get_desired_position(self):
        return 0

    def get_desired_speed(self):
        #index = max([x for x in self.speed_setting.keys() if x < self.state.distance_from_start])
        dfe = self.state.distances_from_edge

        min_dist = max(dfe[9], dfe[10], dfe[11])
        if (min_dist > 190):
            speed = 100
        elif min_dist < 0:
            speed = 10
        else:
           # print(min_dist)
            speed = min_dist + 5

        speed = max(-self.pid.get_action(min_dist), 10)

        return speed

    def get_desired_angle(self):
        return 0

    def get_desired_focus(self):
        return 0