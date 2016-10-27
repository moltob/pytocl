import logging

from pytocl.steering import Steering
from pytocl.analysis import DataLogWriter
from pytocl.car import State, Command, MPS_PER_KMH

from pytocl.acceleration import Acceleration

_logger = logging.getLogger(__name__)


class Driver:
    """Driving logic.

    Implement the driving intelligence in this class by processing the current car state as inputs
    creating car control commands as a response. The ``drive`` function is called periodically
    every 20ms and must return a command within 10ms wall time.
    """

    def __init__(self, logdata=True):
        self.data_logger = DataLogWriter() if logdata else None
        self.accelerator = Acceleration()
        self.steeringControl = Steering()

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
        # command.steering = ((carstate.angle/90.0) - (carstate.distance_from_center * 0))
        # command.steering = self.steerFilter.filter(command.steering)
        command.steering = self.steeringControl.update(carstate)

        # basic acceleration to target speed:
        targetAcceleration = self.accelerator.update(carstate)
        if targetAcceleration < 0:
            command.brake = -targetAcceleration * 0.5
            command.accelerator = 0.0
        else:
            command.accelerator = targetAcceleration
            command.brake = 0.0

        #_logger.info('accelerator: {}'.format(command.accelerator))
        #_logger.info('brake: {}'.format(command.brake))
        #_logger.info('current velocity: {}'.format(carstate.speed_x))
        _logger.info('distance_from_start: {}'.format(carstate.distance_from_start))

        # gear shifting:
        #_logger.info('rpm, gear: {}, {}'.format(carstate.rpm, carstate.gear))
        command.gear = carstate.gear or 1
        if carstate.rpm > 9000 and carstate.gear < 6:
            _logger.info('switching up')
            command.gear = carstate.gear + 1
        elif carstate.rpm < 3000 and carstate.gear > 1:
            _logger.info('switching down')
            command.gear = carstate.gear - 1

        if self.data_logger:
            self.data_logger.log(carstate, command)

        return command
