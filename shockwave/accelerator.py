from pytocl.car import State
from shockwave.plan import Plan


class Accelerator:
    def __init__(self):
        pass

    def get_acceleration(self, state: State, plan: Plan):
        return 0 # -1 to 1
