from pytocl.car import State, CustomData
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
        self.m_p1 = 0
        self.m_p2 = 0
        self.m_p3 = 0

    def control(self, carstate: State, custom_data: CustomData):
        self.speed, self.target_pos = self.control_speed(carstate, custom_data)

        if carstate.distance_raced < 50:
            self.speed = 600
            self.target_pos = 0.5
        elif carstate.distance_raced < 220:
            self.speed = 600
            self.target_pos = 0.3
        elif carstate.distance_raced < 580:
            self.target_pos = 0.4

        return self.speed, self.target_pos

    def control_speed(self, carstate: State, custom_data: CustomData):
        cshape = self.detect_curve(carstate, 90)
        custom_data.cshape = cshape
        #opponent_pos = self.detect_opponent(carstate)
        #if opponent_pos == Side.LEFT:
        #    lane = 0.9
        #elif opponent_pos == Side.RIGHT:
        #    lane = -0.9
        #else:
        #    lane = 0.0 #self.detect_curve_lane(carstate)
        lane = self.detect_curve_lane(carstate)

        m = carstate.distances_from_edge
        m_now = m[9]

        #_logger.info('dist: {}, CURVE: {} -- LANE: {}||| {} || {} || {}'.format(carstate.distance_from_start, cshape, lane, m[8], m[9], m[10]))

        if cshape == 0:
            return 400, lane
        else:
            return 600 - 550*abs(cshape), lane

        self.m_p1 = m_now
        self.m_p2 = m_p1
        self.m_p3 = m_p2

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
        #print(carstate.speed_x, carstate.speed_y)

        if carstate.speed_x > 51:
            shape_cut = 125
        elif carstate.speed_x > 20:
                shape_cut = 95
        elif carstate.speed_x > 10:
            shape_cut = 80
        else:
            shape_cut = 40

        offset = 0

        cshape = abs(m[left+offset] - m[right-offset])
        if cshape > shape_cut:
            cshape = shape_cut
        cshape /= shape_cut
        if carstate.distances_from_egde_valid and m[9] < det_dist:
            if m[left+offset] < m[middle+offset] < m[right-offset]:
                return 1 - cshape
            elif m[left+offset] > m[middle+offset] > m[right-offset]:
                return -1 * (1 - cshape)
            else:
                return 0
        else:
            return 0
