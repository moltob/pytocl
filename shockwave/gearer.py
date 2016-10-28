from pytocl.car import State
import logging

_logger = logging.getLogger(__name__)


class Gearer:
    def __init__(self, plan):
        self.emergency = False
        self.emergencyCounter = 0
        self.plan = plan

    def get_gear(self, state: State):
        if state.gear == 0:
            return 1

        gear = state.gear if state.gear != 0 else 1
        if state.rpm > 9000 and state.gear < 6:
            gear = state.gear + 1
        elif state.rpm < 1000 and state.gear > 2:
            gear = state.gear - 2
        elif state.rpm < 2000 and state.gear > 1:
            gear = state.gear - 1

        if (not state.distances_from_egde_valid) and state.speed_x == 0 and self.plan.get_desired_speed() > 0:
            self.emergency = True

        if (self.emergency == True):
            self.emergencyCounter += 1
            gear = -1
            if self.emergencyCounter > 10:
                self.emergency = False
                self.emergencyCounter = 0

        return gear
