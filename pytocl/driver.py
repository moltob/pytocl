import logging

from pytocl.analysis import DataLogWriter
from pytocl.car import State, Command, MPS_PER_KMH

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
        self.angle_old = 1
        self.currentAngleCorr = 0.3
        self.carstate_old = None

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

    def select_gear(self, carstate: State, command: Command):

        # gear shifting:
        #_logger.info('rpm, gear: {}, {}'.format(carstate.rpm, carstate.gear))
        command.gear = carstate.gear or 1
        if carstate.rpm > 7000 and carstate.gear < 6:
            _logger.info('switching up')
            command.gear = carstate.gear + 1
        elif carstate.rpm < 2000 and carstate.gear > 1:
            _logger.info('switching down')
            command.gear = carstate.gear - 1

    def select_steering(self, carstate: State, command: Command):
        #command.steering = (carstate.angle - carstate.distance_from_center * 0.5)

        steering_angle = (carstate.angle * self.currentAngleCorr)

#        angle_diff_quat = abs(self.angle_old-carstate.angle) / self.angle_old


        if ((abs(self.angle_old-carstate.angle) < 5)):
            pass
        elif (self.angle_old < carstate.angle and self.currentAngleCorr < 1):
            self.currentAngleCorr = self.currentAngleCorr + 0.1#*(angle_diff_quat)
        elif (self.angle_old > carstate.angle and self.currentAngleCorr > 0.3):
            self.currentAngleCorr = self.currentAngleCorr - 0.1#*(angle_diff_quat)

        self.angle_old = carstate.angle

        command.steering = (steering_angle)

    def select_acceleration(self, carstate: State, command: Command):

        acceleration_const = 0.8
        _logger.info('distance_from_start: {}'.format(carstate.distance_from_start))

        if carstate.distance_from_start > 0 and carstate.distance_from_start < 350:
            command.accelerator = acceleration_const
            command.brake = 0
        elif carstate.distance_from_start > 350 and carstate.distance_from_start < 380 and carstate.speed_x > 60 * MPS_PER_KMH:
            command.accelerator = 0
            command.brake = 1
        elif carstate.distance_from_start > 480 and carstate.distance_from_start < 700:
            command.accelerator = acceleration_const
            command.brake = 0
        elif carstate.distance_from_start > 700 and carstate.distance_from_start < 750 and carstate.speed_x > 60 * MPS_PER_KMH:
            command.accelerator = 0
            command.brake = 1
        elif carstate.distance_from_start > 800 and carstate.distance_from_start < 950:
            command.accelerator = acceleration_const
            command.brake = 0
        elif carstate.distance_from_start > 1100 and carstate.distance_from_start < 1400:
            command.accelerator = acceleration_const
            command.brake = 0
        elif carstate.distance_from_start > 1450 and carstate.distance_from_start < 1500 and carstate.speed_x > 60 * MPS_PER_KMH:
            command.accelerator = 0
            command.brake = 1
        elif carstate.distance_from_start > 1580 and carstate.distance_from_start < 1850:
            command.accelerator = acceleration_const
            command.brake = 0
        elif carstate.distance_from_start > 1850 and carstate.distance_from_start < 1950 and carstate.speed_x > 60 * MPS_PER_KMH:
            command.accelerator = 0
            command.brake = 1
        elif carstate.distance_from_start > 1950 and carstate.distance_from_start < 2300:
            command.accelerator = acceleration_const
            command.brake = 0
        elif carstate.distance_from_start > 2300 and carstate.distance_from_start < 2400 and carstate.speed_x > 60 * MPS_PER_KMH:
            command.accelerator = 0
            command.brake = 1
        elif carstate.distance_from_start > 2550 and carstate.distance_from_start < 2650:
            command.accelerator = acceleration_const
            command.brake = 0
        elif carstate.distance_from_start > 2650 and carstate.distance_from_start < 2700 and carstate.speed_x > 60 * MPS_PER_KMH:
            command.accelerator = 0
            command.brake = 1
        elif carstate.distance_from_start > 3050 and carstate.distance_from_start < 3400:
            command.accelerator = acceleration_const
            command.brake = 0
        else:
            command.brake = 0

            if carstate.speed_x < 60 * MPS_PER_KMH:
                self.accelerator += 0.1
            else:
                self.accelerator = 0
            self.accelerator = min(1, self.accelerator)
            self.accelerator = max(-1, self.accelerator)
            command.accelerator = self.accelerator
       # _logger.info('accelerator: {}'.format(command.accelerator))

    def drive(self, carstate: State) -> Command:
        """Produces driving command in response to newly received car state.

        This is a dummy driving routine, very dumb and not really considering a lot of inputs. But
        it will get the car (if not disturbed by other drivers) successfully driven along the race
        track.
        """
        command = Command()

        # steering control:
        self.select_steering(carstate, command)

        # basic acceleration to target speed:
        self.select_acceleration(carstate, command)

        self.select_gear(carstate, command)

        if self.data_logger:
            self.data_logger.log(carstate, command)

        self.angle_old = carstate.angle

        return command
