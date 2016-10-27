from pytocl.pid import PID
from pytocl.car import State


class Steering:
    def __init__(self):
        self.control = PID(0.3, 0.1, 0, Integrator_max=1, Integrator_min=-1)

    def update(self, carstate):
        deltaAngle = max(min(1, (-carstate.angle / 10.0) + (carstate.distance_from_center * 0.4)), -1)
        return self.control.update(deltaAngle)
