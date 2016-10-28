from pytocl.car import State
import logging

_logger = logging.getLogger(__name__)


class Gearer:
    def __init__(self, plan):
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

        return gear
