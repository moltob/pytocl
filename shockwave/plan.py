from pytocl.car import State
import math

from shockwave.pid import PID


class Plan:
    def __init__(self, strategy):
        self.strategy = strategy
        self.state = None
        self.pid = PID(1, 30, 0)

    def get_desired_position(self):
        dfe = self.state.distances_from_edge
        center_index = int(self.state.angle / 10) + 10 if abs(int(self.state.angle / 10)) < 8 else None
        if center_index is None:
            return 0

        if dfe[center_index] < 0:
            return 0

        if dfe[center_index] > 195:
            return 0

        right = False
        if dfe[center_index-1] < dfe[center_index] and dfe[center_index-2] < dfe[center_index]:
            right = True
        left = False
        if dfe[center_index + 1] < dfe[center_index] and dfe[center_index + 2] < dfe[center_index]:
            left = True

        if right and left:
            print("BOTH")
            return 0
        elif right:
            print("RIGHT")
            return -0.5
        elif left:
            print("LEFT")
            return 0.5
        else:
            print("KEINE")
            return 0

        return 0

    def get_desired_speed(self):
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