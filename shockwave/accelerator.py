from pytocl.car import State
from shockwave.pid import PID


class Accelerator:

    def __init__(self, plan):
        self.plan = plan
        self.pid = PID(0.1, 0, 0.003)

    def get_acceleration(self, state: State):
        desired_speed = self.plan.get_desired_speed()
        acceleration = self.pid.get_acceleration(state.speed_x - desired_speed)
        if acceleration > 1:
            acceleration = 1
        elif acceleration < -1:
            acceleration = -1
        return acceleration