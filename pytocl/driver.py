import logging

from pytocl.analysis import DataLogWriter
from pytocl.car import State, Command, MPS_PER_KMH
from .jazzDriver.jazzdriver import JazzDriver
from .jazzDriver.jazzTrackTrainer import JazzTrackTrainer

_logger = logging.getLogger(__name__)


class Driver:
    """Driving logic.

    Implement the driving intelligence in this class by processing the current car state as inputs
    creating car control commands as a response. The ``drive`` function is called periodically
    every 20ms and must return a command within 10ms wall time.
    """

    def __init__(self, logdata=True):
        self.data_logger = DataLogWriter() if logdata else None
        self.accelerator = 0.0
        self.jazzDriver = JazzDriver()
        self.trackTrainer = JazzTrackTrainer()

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
        """Produces driving command in response to newly received car state.

        This is a dummy driving routine, very dumb and not really considering a lot of inputs. But
        it will get the car (if not disturbed by other drivers) successfully driven along the race
        track.
        """
        command = Command()

        # dummy steering control:
        command.steering = (carstate.angle - carstate.distance_from_center * 0.5)

        # basic acceleration to target speed:
        if carstate.speed_x < 50 * MPS_PER_KMH:
            self.accelerator += 0.1
        else:
            self.accelerator = 0
        self.accelerator = min(1, self.accelerator)
        self.accelerator = max(-1, self.accelerator)
        command.accelerator = self.accelerator
#        _logger.info('accelerator: {}'.format(command.accelerator))

        # gear shifting:
#        _logger.info('rpm, gear: {}, {}'.format(carstate.rpm, carstate.gear))
        command.gear = carstate.gear or 1
        if carstate.rpm > 7000 and carstate.gear < 6:
            _logger.info('switching up')
            command.gear = carstate.gear + 1
        elif carstate.rpm < 2000 and carstate.gear > 1:
            _logger.info('switching down')
            command.gear = carstate.gear - 1

        if self.data_logger:
            self.data_logger.log(carstate, command)

        #return self.trackTrainer.drive(carstate)
        return self.jazzDriver.drive(carstate)
