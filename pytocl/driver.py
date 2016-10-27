import logging

from pytocl.analysis import DataLogWriter
from pytocl.car import State, Command, MPS_PER_KMH
from pytocl.pid import PID

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
        self.brake = 0.0
        self.pid_angle = PID(2.5, 0.01, 0.7)
        self.pid_dist = PID(2.5, 0.01, 0.7)
        self.pid_speed = PID(2.5, 0.01, 0.7)

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
        steering_stellgr_angle = (-self.pid_angle.control(carstate.angle, 0) / 180)
        steering_stellgr_dist = self.pid_dist.control(carstate.distance_from_center, 0)

        command.steering = (4*steering_stellgr_angle + steering_stellgr_dist) / 5

        # basic acceleration to target speed:
        #if carstate.speed_x < 40 * MPS_PER_KMH:
        #    self.accelerator += 0.1
        #else:
        #    self.accelerator = 0
        #self.accelerator = min(1, self.accelerator)
        #self.accelerator = max(-1, self.accelerator)


        tar_speed = self.calc_target_speed(carstate)

        speed_control = self.pid_speed.control(carstate.speed_x, tar_speed * MPS_PER_KMH)

        _logger.info('speed_control: {}'.format(speed_control))

        self.accel_and_brake(carstate.speed_x, tar_speed)

        command.accelerator = self.accelerator
        _logger.info('accelerator: {}'.format(command.accelerator))

        command.brake = self.brake

        # gear shifting:
        _logger.info('rpm, gear: {}, {}'.format(carstate.rpm, carstate.gear))
        command.gear = carstate.gear or 1
        if carstate.rpm > 7000 and carstate.gear < 6:
            _logger.info('switching up')
            command.gear = carstate.gear + 1
        elif carstate.rpm < 2000 and carstate.gear > 1:
            _logger.info('switching down')
            command.gear = carstate.gear - 1

        if self.data_logger:
            self.data_logger.log(carstate, command)

        self.last_steering = command.steering

        _logger.info("Distance: " + str(carstate.distance_from_start))

        return command

    def accel_and_brake(self, cur_speed, target_speed):
        if cur_speed < target_speed * MPS_PER_KMH:
            self.accelerator += 0.1
            self.brake = 0
        elif (cur_speed - (target_speed * MPS_PER_KMH)) > 50:
            self.brake += 0.1
            self.accelerator = 0
        elif cur_speed > target_speed * MPS_PER_KMH:
            self.brake = 0.1
            self.accelerator = 0
        else:
            self.accelerator = 0
            self.brake = 0

        self.accelerator = min(1, self.accelerator)
        self.accelerator = max(-1, self.accelerator)
        self.brake = min(1, self.brake)
        self.brake = max(-1, self.brake)

    def calc_target_speed(self, carstate: State):
        if carstate.distances_from_edge[9] < 35:
            return 55
        if carstate.distances_from_edge[9] < 50:
            return 80
        if carstate.distances_from_edge[9] < 100:
            return 100
        if carstate.distances_from_edge[9] < 150:
            return 150
        else:
            return 200