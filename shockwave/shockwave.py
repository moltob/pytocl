import logging
from pytocl.car import State, Command, MPS_PER_KMH
from pytocl.driver import Driver
from shockwave.plan import Plan
from shockwave.stability import Stability
from shockwave.strategy import Strategy

_logger = logging.getLogger(__name__)


class Shockwave(Driver):
    def __init__(self):
        super().__init__()
        self.strategy = Strategy()
        self.plan = Plan(self.strategy)
        self.stability = Stability(self.plan)

    def drive(self, carstate: State) -> Command:
        return self.stability.get_command(carstate)
