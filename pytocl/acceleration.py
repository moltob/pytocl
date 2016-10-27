from pytocl.pid import PID
from pytocl.car import State, MPS_PER_KMH


class Acceleration:
    def __init__(self):
        self.control = PID(0.5, 0.1, 0.2, Integrator_max=20, Integrator_min=-20)
        self.targetVelocity = 21.6

    def update(self, carstate):
        # if carstate.speed_x < (50 * MPS_PER_KMH):
        #    self.targetVelocity += (10 * MPS_PER_KMH)
        # else:
        #    self.targetVelocity -= (10 * MPS_PER_KMH)

        deltaVelocity = (self.targetVelocity - (carstate.speed_x))

        return self.control.update(deltaVelocity)
