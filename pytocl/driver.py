import logging

from pytocl.analysis import DataLogWriter
from pytocl.car import State, Command, MPS_PER_KMH
from pytocl.pid import PID
from pytocl.speedlist import SpeedList
from pytocl.overtakelist import OvertakeList
from pytocl.opponents import Opponents
from pytocl.opponents import Area
from pytocl.filter import *
from math import sqrt
from enum import Enum

_logger = logging.getLogger(__name__)

class OvertakeStates(Enum):
    INIT_OVERTAKE=0
    START_OVERTAKE=1
    IN_OVERTAKE = 2
    END_OVERTAKE = 3

class DriveModeStates(Enum):
    DRIVEMODE_STARTUP=0
    DRIVEMODE_NORMAL=1
    DRIVEMODE_OVERTAKE = 2
    DRIVEMODE_FOLLOW = 3

class Driver:
    """Driving logic.

    Implement the driving intelligence in this class by processing the current car state as inputs
    creating car control commands as a response. The ``drive`` function is called periodically
    every 20ms and must return a command within 10ms wall time.
    """

    def __init__(self, logdata=True):
        self.data_logger = DataLogWriter() if logdata else None
        self.pid_angle = PID(9, 0.05, 0)
        self.pid_dist = PID(0.5, 0.02, 0)
        self.pid_speed = PID(20, 0, 0)
        self.pid_distanceToOpponent = PID(10, 0, 0)
        self.speedlist = SpeedList()
        self.startUpAccelarations = SpeedList()
        self.overtakelist = OvertakeList()
        self.acc_counter = 0
        self.brake_counter = 0
        self.driveMode = DriveModeStates.DRIVEMODE_STARTUP
        self.overtakeState = OvertakeStates.INIT_OVERTAKE
        self.createCorkScrewSpeedlist()
        self.createOvertakeList()
        self.createStartupAccelerationsList()
        self.oponents = Opponents()

    def createStartupAccelerationsList(self):
        self.startUpAccelarations.add(0, 0.3)
        self.startUpAccelarations.add(10, 0.4)
        self.startUpAccelarations.add(20, 0.5)
        self.startUpAccelarations.add(40, 0.7)
        self.startUpAccelarations.add(50, 0.8)
        self.startUpAccelarations.add(50, 0.8)
        self.startUpAccelarations.add(70, 1.0)
        #self.startUpAccelarations.add(60, 0.8)
        #self.startUpAccelarations.add(70, 1.0)

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


    def createOvertakeList(self):
        #self.overtakelist.add(0.5, 0, 250)
        self.overtakelist.add(0.5, 1550, 1900, 100)
        self.overtakelist.add(0.5, 3200, 3600, 0)

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
        # check which drive mode to choose
        bCanOvertake, distanceToGo, brakedist = self.overtakelist.canOvertake(carstate.distance_from_start)
        if carstate.distance_from_center > 1.3 or carstate.distance_from_center <-1.3:
            self.driveMode = 2
        elif self.driveMode == 2:
            self.driveMode = 1

        #if bCanOvertake:
        #    self.driveMode = DriveModeStates.DRIVEMODE_OVERTAKE
        #else:
        #    self.driveMode = DriveModeStates.DRIVEMODE_NORMAL

        self.oponents.update(carstate)
        distanceToFront = self.oponents.dist_to_car(Area.FRONT)

        if distanceToFront == 200:
            self.driveMode = DriveModeStates.DRIVEMODE_NORMAL
        else:
            self.driveMode = DriveModeStates.DRIVEMODE_FOLLOW

        if self.driveMode == DriveModeStates.DRIVEMODE_STARTUP:
            command = self.startDrive(carstate)
        elif self.driveMode == DriveModeStates.DRIVEMODE_NORMAL:
            command = self.optimizedDrive(carstate)
        elif self.driveMode == DriveModeStates.DRIVEMODE_OVERTAKE:
        elif  self.driveMode == 2:
            command = self.recoverDrive(carstate)
        else:
            command = self.overtakeDrive(carstate)
        elif self.driveMode == DriveModeStates.DRIVEMODE_FOLLOW:
            command = self.followDrive(carstate)
        _logger.info('driveMode: {}'.format(self.driveMode))
        _logger.info('distanceToFront: {}'.format(distanceToFront))
        return command

    def overtakeDrive(self, carstate: State) -> Command:
        """overtake mode"""
        bCanOvertake, distanceToGo, brakedist = self.overtakelist.canOvertake(carstate.distance_from_start)

        if self.overtakeState == OvertakeStates.INIT_OVERTAKE:
            self.overtakeState = OvertakeStates.START_OVERTAKE

        _logger.info('bCanOvertake: {}'.format(bCanOvertake))
        _logger.info('distanceToGo: {}'.format(distanceToGo))
        _logger.info('overtakeState: {}'.format(self.overtakeState))

        tar_speed = self.speedlist.getSpeedForDistance(carstate.distance_from_start)

        if self.overtakeState == OvertakeStates.START_OVERTAKE:
            self.overtakeState = OvertakeStates.IN_OVERTAKE
            return self.controlCar(carstate, over_steer=False, oversteer_angle=0, tar_speed=300, K_acc=1.0,
                                   T_acc=20, K_brake=0.8, T_brake=20, center_dist=0.3, k_p_center=1, k_i_center=0.02,
                                   k_d_center=0)
        elif self.overtakeState == OvertakeStates.IN_OVERTAKE:
            if distanceToGo < brakedist:
                self.overtakeState = OvertakeStates.END_OVERTAKE
                return self.controlCar(carstate, over_steer=False, oversteer_angle=0, tar_speed=tar_speed, K_acc=0.8,
                                       T_acc=20, K_brake=0.8, T_brake=20, center_dist=0.0, k_p_center=1, k_i_center=0.02,
                                       k_d_center=0)

            return self.controlCar(carstate, over_steer=False, oversteer_angle=0, tar_speed=300, K_acc=1.0,
                                   T_acc=20, K_brake=0.8, T_brake=20, center_dist=0.3, k_p_center=1, k_i_center=0.02,
                                   k_d_center=0)

        elif self.overtakeState == OvertakeStates.END_OVERTAKE:
            return self.controlCar(carstate, over_steer=False, oversteer_angle=0, tar_speed=tar_speed, K_acc=0.8,
                                   T_acc=20, K_brake=0.8, T_brake=20, center_dist=0.0, k_p_center=1, k_i_center=0.02,
                                   k_d_center=0)
            self.driveMode = DriveModeStates.DRIVEMODE_NORMAL
        pass

    def optimizedDrive(self, carstate: State) -> Command:
        """normal drive mode"""

        _logger.info('distances: {}'.format(carstate.distances_from_edge))
        tar_speed = self.speedlist.getSpeedForDistance(carstate.distance_from_start)
        return self.controlCar(carstate, over_steer=False, oversteer_angle=0, tar_speed=tar_speed, K_acc=0, T_acc=5, K_brake=0, T_brake=25, center_dist=0, k_p_center=0.5, k_i_center=0.02, k_d_center=0)
        pass

    def recoverDrive(self, carstate: State) -> Command:
        tar_speed = self.speedlist.getSpeedForDistance(carstate.distance_from_start % 3608)
        return self.controlCar(carstate, over_steer=False, oversteer_angle=0, tar_speed=max(30,sqrt(carstate.speed_x**2+carstate.speed_y**2)-1)    , K_acc=0, T_acc=5, K_brake=0, T_brake=25, center_dist=0, k_p_center=0.5, k_i_center=0.02, k_d_center=0)
        pass

    def followDrive(self, carstate: State) -> Command:
        """normal drive mode"""

        distanceToFront = self.oponents.dist_to_car(Area.FRONT)
        pidResult = self.pid_distanceToOpponent.control(distanceToFront, 5)

        if pidResult < 0:
            return self.controlCar(carstate, over_steer=False, oversteer_angle=0, tar_speed=100, K_acc=0.8, T_acc=5, K_brake=0.5, T_brake=25, center_dist=0, k_p_center=0.5, k_i_center=0.02, k_d_center=0)
        else:
            return self.controlCar(carstate, over_steer=False, oversteer_angle=0, tar_speed=100, K_acc=0.5, T_acc=5,
                                   K_brake=0.8, T_brake=25, center_dist=0, k_p_center=0.5, k_i_center=0.02,
                                   k_d_center=0)

        _logger.info('distanceToFront: {}'.format(distanceToFront))
        _logger.info('pidResult: {}'.format(pidResult))

        pass

    def startDrive(self, carstate: State) -> Command:
        """optimized code for startup behaviour"""

        if carstate.distance_raced > 80 and self.driveMode == 0:
            self.driveMode = 1

        tar_speed = self.speedlist.getSpeedForDistance(carstate.distance_from_start % 3608)
        acceleration = self.startUpAccelarations.getSpeedForDistance(carstate.distance_from_start)
        _logger.info('acceleration: {}'.format(acceleration))
        return self.controlCar(carstate, over_steer=False, oversteer_angle=0, tar_speed=tar_speed, K_acc=acceleration, T_acc=20, K_brake=0, T_brake=20, center_dist=0, k_p_center=0.5, k_i_center=0.02, k_d_center=0)
        pass

    def controlCar(self, carstate: State, over_steer, oversteer_angle, tar_speed, K_acc, T_acc, K_brake, T_brake, center_dist, k_p_center, k_i_center, k_d_center) -> Command:
        """basic function to control car on street"""
        command = Command()

        command.steering = self.calc_steering(carstate, center_dist, k_p_center, k_i_center, k_d_center, oversteer_angle)
        _logger.info('command.steering: {}'.format(command.steering))

        command.accelerator, command.brake = self.calc_accel_and_brake(carstate, command.steering, tar_speed, K_acc, T_acc, K_brake, T_brake)

        #_logger.info('accelerator: {}'.format(command.accelerator))
        #_logger.info('brake: {}'.format(command.brake))

        #_logger.info('rpm, gear: {}, {}'.format(carstate.rpm, carstate.gear))
        command.gear = self.shift_gears(carstate)

        if self.data_logger:
            self.data_logger.log(carstate, command)

        _logger.info("Distance: " + str(carstate.distance_from_start))

        return command

    def calc_steering(self, carstate: State, center_dist, k_p_center, k_i_center, k_d_center, oversteer_angle=0):
        steering_stellgr_angle = (-self.pid_angle.control(carstate.angle, 0) / 180)


        self.pid_dist.set_params(k_p_center, k_i_center, k_d_center)
        steering_stellgr_dist = self.pid_dist.control(carstate.distance_from_center, center_dist)


        if oversteer_angle > 0:
            steering = oversteer_angle
        else:
            steering = (3*steering_stellgr_angle + steering_stellgr_dist) / 3


        return steering

    def calc_accel_and_brake(self, carstate, steering, tar_speed, K_acc, T_acc, K_brake, T_brake):
        if abs(steering) < 0.1:
            if carstate.distance_raced > 80:
                K_acc = 1.0
            else:
                K_acc = 0.75
            K_brake = 1
        elif abs(steering) < 0.3:
            if K_acc == 0:
                K_acc = 0.8

            if K_brake == 0:
                K_brake = 1
        else:
            if K_acc == 0:
                K_acc = 0.5

            if K_brake == 0:
                K_brake = 1

        #tar_speed = self.calc_target_speed(carstate)
        #tar_speed = self.speedlist.getSpeedForDistance(carstate.distance_from_start % 3608)

        #speed_control = self.pid_speed.control(carstate.speed_x, tar_speed * MPS_PER_KMH)

        #_logger.info('speed_control: {}'.format(speed_control))
        #speed_control = speed_control / MPS_PER_KMH
        speed_control = (tar_speed * MPS_PER_KMH) - carstate.speed_x

        if speed_control > 0:
            self.acc_counter += 1
            accelerator = pt1up(K_acc, T_acc, self.acc_counter)
            #self.accelerator = min(100,speed_control) / 100
            brake = 0
            self.brake_counter = 0
        elif speed_control < 0:
            #self.brake = -(max(-100,speed_control) / 100)
            self.brake_counter += 1
            brake = pt1up(K_brake, T_brake, self.brake_counter)
            accelerator = 0
            self.acc_counter = 0
        else:
            accelerator = 0
            brake = 0
            self.brake_counter = 0
            self.acc_counter = 0

        accelerator = min(1, accelerator)
        accelerator = max(-1, accelerator)
        brake = min(1, brake)
        brake = max(-1, brake)

        return accelerator, brake

    def shift_gears(self, carstate):
        gear = carstate.gear or 1
        if carstate.rpm > 8500 and carstate.gear < 6:
            #_logger.info('switching up')
            gear = carstate.gear + 1
        elif carstate.rpm < 5000 and carstate.gear > 1:
            #_logger.info('switching down')
            gear = carstate.gear - 1

        return gear

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
