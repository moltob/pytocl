import logging

from pytocl.analysis import DataLogWriter
from pytocl.car import State, Command, MPS_PER_KMH

_logger = logging.getLogger(__name__)

class JazzTrackTrainer:
    def __init__(self, logdata=True):
        self.data_logger = DataLogWriter() if logdata else None
        self.acceleration = 0
        self.brake = 0
        self.angle = 0
        self.gear = 1

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
        command = Command()
        _logger.info('switching up')

        keyUp = False
        keyDown = False
        keyLeft = False
        keyRight = False

        if keyUp:
            self.acceleration = 1
        else:
            self.acceleration = 0

        if keyDown:
            self.brake = 1
        else:
            self.brake = 0

        if keyLeft:
            self.angle -= 0.1
        if keyRight:
            self.angle += 0.1
        self.angle = min(1, self.angle)
        self.angle = max(-1, self.angle)

        # gear shifting:
        _logger.info('rpm, gear: {}, {}'.format(carstate.rpm, carstate.gear))
        command.gear = carstate.gear or 1
        if carstate.rpm > 7000 and carstate.gear < 6:
            _logger.info('switching up')
            command.gear = carstate.gear + 1
        elif carstate.rpm < 2000 and carstate.gear > 1:
            _logger.info('switching down')
            command.gear = carstate.gear - 1

        command.accelerator = self.acceleration
        command.brake = self.brake
        command.steering = self.angle

        if self.data_logger:
            self.data_logger.log(carstate, command)

        return command