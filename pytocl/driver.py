import logging

from pytocl.car import State, Command, MPS_PER_KMH, CustomData

from pytocl.stability import StabilityController
from pytocl.strategy import StrategyController
from pytocl.emergency import EmergencyController

_logger = logging.getLogger(__name__)


class Driver:
    """Driving logic.

    Implement the driving intelligence in this class by processing the current car state as inputs
    creating car control commands as a response. The ``drive`` function is called periodically
    every 20ms and must return a command within 10ms wall time.
    """

    def __init__(self):
        self.stability_controller = StabilityController()
        self.strategy_controller = StrategyController()
        self.emergency_controller = EmergencyController()

    @property
    def range_finder_angles(self):
        """Iterable of 19 fixed range finder directions [deg].

        The values are used once at startup of the client to set the directions of range finders.
        During regular execution, a 19-valued vector of track distances in these directions is
        returned in ``state.State.tracks``.
        """
        return -90, -75, -60, -45, -30, -20, -15, -10, -5, 0, 5, 10, 15, 20, 30, 45, 60, 75, 90
        #return -90, -75, -60, -45, -30, -20, -15, -10, -2, 0, 2, 10, 15, 20, 30, 45, 60, 75, 90

    def on_shutdown(self):
        """Server requested driver shutdown.

        Optionally implement this event handler to clean up or write data before the application is
        stopped.
        """
        pass

    def drive(self, carstate: State) -> Command:
        """Produces driving command in response to newly received car state.

        This is a dummy driving routine, very dumb and not really considering a lot of inputs. But
        it will get the car (if not disturbed by other drivers) successfully driven along the race
        track.
        """
        (strategy_speed, strategy_target_pos) = self.strategy_controller.control(carstate)
        next_command = self.stability_controller.control(strategy_speed, strategy_target_pos, carstate)

        self.emergency_controller.control(carstate, next_command)

        return next_command
