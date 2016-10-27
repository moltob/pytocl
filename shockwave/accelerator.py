from pytocl.car import State


class Accelerator:

    FULL_ACC_ANGLE = 20.0
    FULL_BREAK_ANGLE = 45.0

    def __init__(self, plan):
        self.plan = plan
        self.pid = AcceleratorPID(0.5, 0, 0)

    def get_acceleration(self, state: State):
        desired_speed = self.plan.get_desired_speed()
        acceleration = self.pid.get_acceleration(state.speed_x - desired_speed)
        return acceleration


class AcceleratorPID:
    def __init__(self, kp, kd, ki):
        self.kp, self.kd, self.ki = kp, kd, ki
        self.last_e = None
        self.last_es = []

    def get_acceleration(self, e):
        if self.last_e is None:
            self.last_e = e

        self.last_es.append(e)
        if len(self.last_es) > 20:
            self.last_es.pop(0)

        de = e - self.last_e
        ie = sum(self.last_es)

        self.last_e = e
        out = -self.kp*e - self.kd*de - self.ki*ie

        return out
