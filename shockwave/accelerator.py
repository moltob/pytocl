from pytocl.car import State
from shockwave.pid import PID
import math

class Accelerator:

    def __init__(self, plan):
        self.plan = plan
        self.pid = PID(0.1, 0, 0.003)

    def get_acceleration(self, state: State):
        desired_speed = self.plan.get_desired_speed()
        speed = math.sqrt(state.speed_x * state.speed_x + state.speed_y * state.speed_y + state.speed_z * state.speed_z)
        acceleration = self.pid.get_action(speed - desired_speed)
        if acceleration > 1:
            acceleration = 1
        elif acceleration < -1:
            acceleration = -1

        if min(state.wheel_velocities) == 0.0 and acceleration == -1:
            acceleration = 0.5

        return acceleration