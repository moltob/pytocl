from pytocl.car import State
import logging

from shockwave.pid import PID

_logger = logging.getLogger(__name__)


class Steerer:
    def __init__(self, plan):
        self.plan = plan
        self.pid = PID(0.3, 20, 0)
        self.angle = 0

    def get_steering_angle(self, state: State):
        self.angle = self.pid.get_steering(state.distance_from_center - self.plan.get_desired_position())
        if self.angle > 1:
            self.angle = 1
        elif self.angle < -1:
            self.angle = -1
        return self.angle
