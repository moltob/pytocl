import logging

from pytocl.analysis import DataLogWriter
from pytocl.car import State, Command, MPS_PER_KMH
from pytocl.pid import PID
from pytocl.speedlist import SpeedList
from pytocl.filter import *

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
        self.pid_angle = PID(9, 0.05, 0)
        self.pid_dist = PID(0.5, 0.02, 0)
        self.pid_speed = PID(20, 0, 0)
        self.speedlist = SpeedList()
        self.createCorkScrewSpeedlist()
        self.acc_counter = 0
        self.brake_counter = 0

    def createCorkScrewSpeedlist(self):
        self.speedlist.add(20, 200)
        self.speedlist.add(160, 160)
        self.speedlist.add(180, 150)
        self.speedlist.add(210, 180)
        self.speedlist.add(350, 150)
        self.speedlist.add(365, 110)
        self.speedlist.add(380, 100)
        self.speedlist.add(405, 95)
        self.speedlist.add(450, 100)
        self.speedlist.add(505, 130)
        self.speedlist.add(520, 170)
        self.speedlist.add(700, 120)
        self.speedlist.add(720, 100)
        self.speedlist.add(730, 100)
        self.speedlist.add(780, 120)
        self.speedlist.add(795, 150)
        self.speedlist.add(805, 200)
        self.speedlist.add(970, 150)
        self.speedlist.add(980, 130)
        self.speedlist.add(990, 120)
        self.speedlist.add(1020, 150)
        self.speedlist.add(1050, 180)
        self.speedlist.add(1200, 160)
        self.speedlist.add(1250, 200)
        self.speedlist.add(1430, 150)
        self.speedlist.add(1450, 130)
        self.speedlist.add(1470, 120)
        self.speedlist.add(1550, 150)
        self.speedlist.add(1600, 180)
        self.speedlist.add(1650, 220)
        self.speedlist.add(1850, 160)
        self.speedlist.add(1880, 140)
        self.speedlist.add(1890, 120)
        self.speedlist.add(1900, 110)
        self.speedlist.add(1905, 95)
        self.speedlist.add(1940, 95)
        self.speedlist.add(1950, 150)
        self.speedlist.add(2020, 130)
        self.speedlist.add(2030, 190)
        self.speedlist.add(2300, 160)
        self.speedlist.add(2320, 140)
        self.speedlist.add(2400, 80)
        self.speedlist.add(2430, 65)
        self.speedlist.add(2460, 55)
        self.speedlist.add(2490, 90)
        self.speedlist.add(2500, 130)
        self.speedlist.add(2590, 170)
        self.speedlist.add(2650, 135)
        self.speedlist.add(2750, 210)
        self.speedlist.add(2800, 180)
        self.speedlist.add(2850, 150)
        self.speedlist.add(2880, 130)
        self.speedlist.add(2900, 120)
        self.speedlist.add(3010, 210)
        self.speedlist.add(3180, 150)
        self.speedlist.add(3200, 110)
        self.speedlist.add(3210, 80)
        self.speedlist.add(3250, 65)
        self.speedlist.add(3290,150)
        self.speedlist.add(3320,200)
        self.speedlist.add(3580,160)


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

        tar_speed = self.speedlist.getSpeedForDistance(carstate.distance_from_start % 3608)
        return self.controlCar(carstate, tar_speed, 0.5, 5, 0.5, 25)

    def controlCar(self, carstate: State, tar_speed, K_acc, T_acc, K_brake, T_brake) -> Command:
        """basic function to control car on street"""
        command = Command()

        # dummy steering control:
        steering_stellgr_angle = (-self.pid_angle.control(carstate.angle, 0) / 180)
        steering_stellgr_dist = self.pid_dist.control(carstate.distance_from_center, 0)

        command.steering = (3*steering_stellgr_angle + steering_stellgr_dist) / 3

        if abs(command.steering) < 0.1:
            if carstate.distance_raced > 80:
                K_acc = 1.0
            else:
                K_acc = 0.75

            K_brake = 1
        else:
            K_acc = 0.5
            K_brake = 1

        #tar_speed = self.calc_target_speed(carstate)
        #tar_speed = self.speedlist.getSpeedForDistance(carstate.distance_from_start % 3608)

        #speed_control = self.pid_speed.control(carstate.speed_x, tar_speed * MPS_PER_KMH)

        #_logger.info('speed_control: {}'.format(speed_control))
        #speed_control = speed_control / MPS_PER_KMH
        speed_control = (tar_speed * MPS_PER_KMH) - carstate.speed_x

        if speed_control > 0:
            self.acc_counter += 1
            self.accelerator = pt1up(K_acc, T_acc, self.acc_counter)
            #self.accelerator = min(100,speed_control) / 100
            self.brake = 0
            self.brake_counter = 0
        elif speed_control < 0:
            #self.brake = -(max(-100,speed_control) / 100)
            self.brake_counter += 1
            self.brake = pt1up(K_brake, T_brake, self.brake_counter)
            self.accelerator = 0
            self.acc_counter = 0
        else:
            self.accelerator = 0
            self.brake = 0
            self.brake_counter = 0
            self.acc_counter = 0

        self.accelerator = min(1, self.accelerator)
        self.accelerator = max(-1, self.accelerator)
        self.brake = min(1, self.brake)
        self.brake = max(-1, self.brake)

        #self.accel_and_brake(carstate.speed_x, tar_speed)

        command.accelerator = self.accelerator
        #_logger.info('accelerator: {}'.format(command.accelerator))

        command.brake = self.brake
        #_logger.info('brake: {}'.format(command.brake))
        # gear shifting:
        #_logger.info('rpm, gear: {}, {}'.format(carstate.rpm, carstate.gear))
        command.gear = carstate.gear or 1
        if carstate.rpm > 8500 and carstate.gear < 6:
            #_logger.info('switching up')
            command.gear = carstate.gear + 1
        elif carstate.rpm < 5000 and carstate.gear > 1:
            #_logger.info('switching down')
            command.gear = carstate.gear - 1

        if self.data_logger:
            self.data_logger.log(carstate, command)

        _logger.info("Distance: " + str(carstate.distance_from_start))

        return command

    def calc_target_speed(self, carstate: State):
        if carstate.distances_from_edge[9] < 20:
            return 50
        if carstate.distances_from_edge[9] < 35:
            return 75
        if carstate.distances_from_edge[9] < 50:
            return 120
        if carstate.distances_from_edge[9] < 100:
            return 180
        if carstate.distances_from_edge[9] < 150:
            return 220
        else:
            return 260
