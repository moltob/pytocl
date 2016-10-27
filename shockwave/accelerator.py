from pytocl.car import State
from shockwave.plan import Plan


class Accelerator:
    def __init__(self, plan):
        self.plan = plan

    def get_acceleration(self, state: State):
        return 0 # -1 to 1
