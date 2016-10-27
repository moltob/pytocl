from pytocl.pid import PID
from pytocl.car import State, MPS_PER_KMH


class Acceleration:
    def __init__(self):
        self.control = PID(0.6, 0.1, 0.6, Integrator_max=20, Integrator_min=-20)
        self.targetVelocity = 20.0

    def update(self, carstate):
        deltaAngle = max(min(1, (carstate.angle / 10.0) - (carstate.distance_from_center * 0.4)), -1)

        self.targetVelocity = max(20, ((1.0 - abs(deltaAngle)) * 30.0))

        deltaVelocity = (self.targetVelocity - (carstate.speed_x))

        return self.control.update(deltaVelocity)
