from pytocl.car import State
import logging

_logger = logging.getLogger(__name__)


class Steerer:
    def __init__(self, plan):
        self.plan = plan
        self.pid = SteeringPID(0.3, 20, 0)
        self.angle = 0

    def get_steering_angle(self, state: State):
        self.angle = self.pid.get_steering(state.distance_from_center - self.plan.get_desired_position())
        if self.angle > 1:
            self.angle = 1
        elif self.angle < -1:
            self.angle = -1
        return self.angle


class SteeringPID:
    def __init__(self, kp, kd, ki):
        self.kp, self.kd, self.ki = kp, kd, ki
        self.last_e = None
        self.last_es = []

    def get_steering(self, e):
        if self.last_e is None:
            self.last_e = e

        self.last_es.append(e)
        if len(self.last_es) > 20:
            self.last_es.pop(0)

        de = e - self.last_e
        ie = sum(self.last_es)

        self.last_e = e
        out = -self.kp*e -self.kd*de - self.ki*ie

        return out
