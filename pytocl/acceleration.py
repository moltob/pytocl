from pytocl.pid import PID
from pytocl.car import State, MPS_PER_KMH


class Acceleration:
    def __init__(self):
        self.control = PID(0.5, 0.1, 0.2, Integrator_max=1, Integrator_min=-1)
        self.deltaAcceleration = 0.0

    def update(self, carstate):
        if carstate.speed_x < (50 * MPS_PER_KMH):
            self.deltaAcceleration += 0.1
        else:
            self.deltaAcceleration = 0

        self.control.update(self.deltaAcceleration)
