from pytocl.car import State
import logging
from enum import Enum

_logger = logging.getLogger(__name__)


class Curve(Enum):
    """Stereotype of a component."""

    NONE = 0
    LEFT = 1
    RIGHT = 2


class StrategyController:
    def __init__(self):
        self.speed = 0
        self.target_pos = 0

    def control(self, carstate: State):
        self.speed = self.control_speed(carstate)

        return self.speed, self.target_pos

    def control_speed(self, carstate: State):
        curve = self.detect_curve(carstate)
        if curve is Curve.NONE:
            return 400
        else:
            return 60

    def detect_curve(self, carstate: State):
        m = carstate.distances_from_edge
        if carstate.distances_from_egde_valid and m[9] > 0 and m[9] < 150:
            if m[8] < m[9] < m[10]:
                return Curve.RIGHT
            elif m[8] > m[9] > m[10]:
                return Curve.LEFT
            else:
                return Curve.NONE
        else:
            return Curve.NONE
