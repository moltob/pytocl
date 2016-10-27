from pytocl.car import State
import logging
from enum import Enum

_logger = logging.getLogger(__name__)


class Side(Enum):
    """Stereotype of a component."""

    NONE = 0
    LEFT = 1
    RIGHT = 2


class StrategyController:
    def __init__(self):
        self.speed = 0
        self.target_pos = 0

    def control(self, carstate: State):
        self.speed, self.target_pos = self.control_speed(carstate)

        return self.speed, self.target_pos

    def control_speed(self, carstate: State):
        cshape = self.detect_curve(carstate, 90)
        #opponent_pos = self.detect_opponent(carstate)
        #if opponent_pos == Side.LEFT:
        #    lane = 0.9
        #elif opponent_pos == Side.RIGHT:
        #    lane = -0.9
        #else:
        #    lane = 0.0 #self.detect_curve_lane(carstate)
        lane = self.detect_curve_lane(carstate)

        m = carstate.distances_from_edge
        #_logger.info('dist: {}, CURVE: {} -- LANE: {}||| {} || {} || {}'.format(carstate.distance_from_start, cshape, lane, m[8], m[9], m[10]))
        if cshape == 0:
            return 400, lane
        else:
            return 600 - 550*abs(cshape), lane

    def detect_opponent(self, carstate: State):
        oppenent_pos = Side.NONE
        if carstate.opponents[16] < 20:
            oppenent_pos = Side.LEFT
        elif carstate.opponents[19] < 20:
            oppenent_pos = Side.RIGHT
        return oppenent_pos

    def detect_curve_lane(self, carstate):
        cshape = self.detect_curve(carstate, 27)
        if cshape != 0:
            if cshape < 0:
                cshape = 0.9
            else:
                cshape = -1.06
        """else:
            cshape = self.detect_curve(carstate, 180)
            if cshape > 0:
                cshape = 0
            else:
                cshape = -0"""
        return cshape

    def detect_curve(self, carstate: State, det_dist):
        m = carstate.distances_from_edge
        left = 8
        middle = 9
        right = 10

        """if carstate.angle > 5:
            offset = -1
        elif carstate.angle < -5:
            offset = 1
        else:"""

        offset = 0

        cshape = abs(m[left+offset] - m[right-offset])
        if cshape > 100:
            cshape = 100
        cshape /= 100
        if carstate.distances_from_egde_valid and m[9] < det_dist:
            if m[left+offset] < m[middle+offset] < m[right-offset]:
                return 1 - cshape
            elif m[left+offset] > m[middle+offset] > m[right-offset]:
                return -1 * (1 - cshape)
            else:
                return 0
        else:
            return 0
