import logging

from pytocl.analysis import DataLogWriter
from pytocl.car import State, Command, MPS_PER_KMH
from .vehicleControl import VehicleControl
from .trajectoryPlanner import TrajectoryPlanner

_logger = logging.getLogger(__name__)

class JazzDriver:
    def __init__(self, logdata=True):
        self.data_logger = DataLogWriter() if logdata else None
        self.accelerator = 0.0
        self.trajectoryPlanner = TrajectoryPlanner()
        self.vehicleControl = VehicleControl()

    @property
    def range_finder_angles(self):
        """Iterable of 19 fixed range finder directions [deg].

        The values are used once at startup of the client to set the directions of range finders.
        During regular execution, a 19-valued vector of track distances in these directions is
        returned in ``state.State.tracks``.
        """
        return -90, -75, -60, -45, -30, -20, -15, -10, -5, 0, 5, 10, 15, 20, 30, 45, 60, 75, 90

    def on_shutdown(self):
        """Server requested driver shutdown.

        Optionally implement this event handler to clean up or write data before the application is
        stopped.
        """
        if self.data_logger:
            self.data_logger.close()
            self.data_logger = None

    def drive(self, carstate: State) -> Command:

        _logger.info('switching up')

        coordinate = self.trajectoryPlanner.update(carstate)
        command = self.vehicleControl.driveTo(coordinate, carstate)

        if self.data_logger:
            self.data_logger.log(carstate, command)

        return command