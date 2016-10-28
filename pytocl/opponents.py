from pytocl.car import State
from enum import Enum
import numpy as np


class Area(Enum):
    FRONT = (17, 18)
    FRONT_LEFT = (15, 16)
    FRONT_RIGHT = (19, 20)
    LEFT = (4, 14)
    RIGHT = (21, 31)
    REAR_LEFT = (1, 3)
    REAR_RIGHT = (32, 34)
    REAR = (35, 0)

    def __init__(self, begin, end):
        self.begin = begin
        self.end = end


class Opponents:
    def __init__(self):
        self.opponents_diff = np.array([])
        self.opponents = np.array([0 for i in range(36)])

    def update(self, carstate: State):
        for i in range(0, 36):
            self.opponents_diff = carstate.opponents[i] - self.opponents[i]

        self.opponents = np.array(carstate.opponents)

    def dist_to_car(self, area: Area):
        if area == Area.REAR:
            return min(self.opponents[[area.begin,area.end]])
        else:
            return min(self.opponents[area.begin:area.end])

    def diff_to_car(self, area: Area):
        if area == Area.REAR:
            return min(self.opponents_diff[[area.begin,area.end]])
        else:
            return min(self.opponents_diff[area.begin:area.end])




