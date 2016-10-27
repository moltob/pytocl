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

    def on_shutdown(self):
        """Server requested driver shutdown.

        Optionally implement this event handler to clean up or write data before the application is
        stopped.
        """
        if self.data_logger:
            self.data_logger.close()
            self.data_logger = None

    def drive(self, carstate: State) -> Command:

        coordinate = self.trajectoryPlanner.update(carstate)
        command = self.vehicleControl.driveTo(coordinate, carstate)

        if self.data_logger:
            self.data_logger.log(carstate, command)

        return command