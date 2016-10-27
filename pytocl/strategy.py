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
        pass

    def control(self, carstate: State):
        curve = self.detect_curve(carstate)
        return ()

    def detect_curve(self, carstate: State):
        m = carstate.distances_from_edge
        if carstate.distances_from_egde_valid and m[9] < 150:
            if m[8] < m[9] < m[10]:
                return Curve.RIGHT
            elif m[8] > m[9] > m[10]:
                return Curve.LEFT
            else:
                return Curve.NONE
        else:
            return Curve.NONE

    def emergency_break(self, carstate: State):
        m = carstate.distances_from_edge
        if carstate.distances_from_egde_valid and m[9] < 20:
            return True
        else:
            return False


