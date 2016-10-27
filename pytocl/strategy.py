from pytocl.car import State, CustomData
import logging

_logger = logging.getLogger(__name__)


class StrategyController:
    def __init__(self):
        self.speed = 0
        self.target_pos = 0

    def control(self, carstate: State, custom_data: CustomData):
        self.speed = self.control_speed(carstate, custom_data)

        return self.speed, self.target_pos

    def control_speed(self, carstate: State, custom_data: CustomData):
        cshape = self.detect_curve(carstate)
        custom_data.cshape = cshape
        if cshape == 0:
            return 400
        else:
            return 600 - 550*abs(cshape)

    def detect_curve(self, carstate: State):
        m = carstate.distances_from_edge
        cshape = abs(m[8] - m[10])
        if cshape > 100:
            cshape = 100
        cshape /= 100
        if carstate.distances_from_egde_valid and m[9] < 90:
            if m[8] < m[9] < m[10]:
                return 1 - cshape
            elif m[8] > m[9] > m[10]:
                return -1 * (1 - cshape)
            else:
                return 0
        else:
            return 0

    def emergency_break(self, carstate: State):
        m = carstate.distances_from_edge
        if carstate.distances_from_egde_valid and m[9] < 20:
            return True
        else:
            return False


