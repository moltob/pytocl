from pytocl.pid import PID
from pytocl.car import State
import logging

_logger = logging.getLogger(__name__)

class Steering:
    CENTER = 0
    LEFT = -1
    RIGHT = 1

    def __init__(self):
        self.control = PID(0.7, 0.05, 0, Integrator_max=1, Integrator_min=-1)
        self.track_position = self.CENTER
        # self.control = PID(1, 0, 0)

    def select_track_position(self, carstate: State):
        if carstate.distance_from_start > 1500:
            self.track_position = self.RIGHT
        else:
            self.track_position = self.LEFT

    def update(self, carstate: State, side):
        # self.select_track_position(carstate)
        self.track_position = side
        if carstate.distances_from_egde_valid:
            if self.track_position == self.LEFT:
                distance_error = 1.5 - carstate.distances_from_edge[0]
            elif self.track_position == self.RIGHT:
                distance_error = -1.5 + carstate.distances_from_edge[18]
            else:
                distance_error = carstate.distance_from_center * 8
        else:
            if self.track_position == self.LEFT:
                distance_error = -1.5 + carstate.distance_from_center * 8
            elif self.track_position == self.RIGHT:
                distance_error = -1.5 + carstate.distance_from_center * 8
            else:
                distance_error = carstate.distance_from_center * 8

        _logger.info('distance_from_start {}'.format(carstate.distance_from_start))
        deltaAngle = max(min(0.7, (carstate.angle / 10.0) - distance_error * 0.1), -0.7)
        return self.control.update(deltaAngle)

# import math
# math.radiand(grad)
# math.cos(math.radiand(grad))
# winkel + entfernung auf abstand: length * math.cos(math.radiand(winkel))
