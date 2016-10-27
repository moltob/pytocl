from pytocl.car import Command, State
from shockwave.accelerator import Accelerator
from shockwave.gearer import Gearer
from shockwave.steerer import Steerer
import logging

_logger = logging.getLogger(__name__)

class Stability:
    def __init__(self, plan):
        self.plan = plan
        self.steerer = Steerer(self.plan)
        self.accelerator = Accelerator(self.plan)
        self.gearer = Gearer(self.plan)

    def get_command(self, state: State) -> Command:
        self.plan.state = state
        command = Command()
        command.steering = self.steerer.get_steering_angle(state)

        ac = self.accelerator.get_acceleration(state)
        command.accelerator = ac if ac > 0 else 0
        command.brake = -ac if ac < 0 else 0

        command.gear = self.gearer.get_gear(state)
        command.focus = 0

        _logger.info("Distance %d", state.distance_from_start)

        return command


