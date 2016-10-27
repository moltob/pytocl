from pytocl.car import State
from shockwave.plan import Plan


class Accelerator:

    FULL_ACC_ANGLE = 20.0
    FULL_BREAK_ANGLE = 45.0

    def __init__(self, plan):
        self.plan = plan

    def get_acceleration(self, state: State, plan: Plan):

        acceleration = 0.0

        if state.angle < abs(self.FULL_ACC_ANGLE):
            acceleration = 1.0
        elif state.angle > abs(self.FULL_BREAK_ANGLE):
            acceleration = -1.0

        # Make sure, acceleration is within bounds -1, 1
        if (acceleration < 0):
            acceleration = max(-1, acceleration)
        else:
            acceleration = min(1, acceleration)

        return acceleration
