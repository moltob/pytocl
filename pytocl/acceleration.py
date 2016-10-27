from pytocl.pid import PID
from pytocl.car import State, MPS_PER_KMH


class Acceleration:
    def __init__(self):
        self.control = PID()

    def update(self, carstate: State):
        if carstate.speed_x < 50 * MPS_PER_KMH:
            self.control += 0.1
        else:
            self.control = 0

        self.control = min(1, self.control)
        self.control = max(-1, self.control)
