import logging
import math

from pytocl.analysis import DataLogWriter
from pytocl.car import State, Command, MPS_PER_KMH

_logger = logging.getLogger(__name__)


class Pid:
    def __init__(self):
        self.previous_error = 0
        self.integral = 0

    def calc(self, setpoint, measured, dt, Kp, Kd, Ki):
        error = setpoint - measured
        self.integral = self.integral + error * dt
        derivative = (error - self.previous_error) / dt
        output = Kp * error + Kd * derivative + Ki * self.integral
        self.previous_error = error
        return output



class Curve:
    def __init__(self, startPoint, endPoint, speed):
        self.sp = startPoint
        self.ep = endPoint
        self.spe = speed

    def startPoint(self):
        return self.sp

    def endPoint(self):
        return self.ep

    def speed(self):
        return self.spe

    def speedCalculation(self):
        if(self.difficulty == 0):
            return 60
        elif(self.difficulty == 1):
            return 80
        elif(self.difficulty == 2):
            return 90
        elif (self.difficulty == 3):
            return 100
        elif (self.difficulty == 4):
            return 110
        else:
            return 90

class Driver:
    """Driving logic.

    Implement the driving intelligence in this class by processing the current car state as inputs
    creating car control commands as a response. The ``drive`` function is called periodically
    every 20ms and must return a command within 10ms wall time.
    """

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
        return self.drive_dani1(carstate)

    def __init__(self, logdata=True):
        self.data_logger = DataLogWriter() if logdata else None
        self.accelerator = 0.0
        self.dt = 0.020
        self.pidSpeed = Pid()
        self.pidAngle = Pid()
        self.pidDistCenter = Pid()

        self.timeMsec = 0
        self.curves = list()
        self.speedSetPoint = 0.0

        c1 = Curve(350, 500, 80)
        self.curves.append(c1)

        c2 = Curve(700, 750, 90)
        self.curves.append(c2)

        c3 = Curve(970, 1100, 140)
        self.curves.append(c3)

        c4 = Curve(1430, 1550, 100)
        self.curves.append(c4)

        c5 = Curve(1880, 1940, 90)
        self.curves.append(c5)

        c6pre = Curve(2300, 2350, 150)
        self.curves.append(c6pre)

        c6pre2 = Curve(2350, 2400, 120)
        self.curves.append(c6pre2)

        c6 = Curve(2400, 2500, 60)
        self.curves.append(c6)

        c7 = Curve(2600, 2700, 120)
        self.curves.append(c7)

        c8 = Curve(2900, 3000, 130)
        self.curves.append(c8)

        c9 = Curve(3200, 3285, 70)
        self.curves.append(c9)



    def drive_dani1(self, carstate: State) -> Command:
        """Produces driving command in response to newly received car state.

        This is a dummy driving routine, very dumb and not really considering a lot of inputs. But
        it will get the car (if not disturbed by other drivers) successfully driven along the race
        track.
        """
        command = Command()

        self.timeMsec = self.timeMsec + 20
        printDistance = False
        if(self.timeMsec % 1000 == 0):
            printDistance = True

        # dummy steering control:
        #distCenterKp = 10.0
        distCenterKp = 2.5
        distCenterKd = 4.0
        distCenterKi = 0.0 #10.0

        speedKp = 15.0
        speedKd = 0.0
        speedKi = 0.0

        #angleKp = 0.07
        angleKp = 0.07
        angleKd = 0.0
        angleKi = 0.0


        trackPos = carstate.distance_from_center
        speed = math.sqrt(carstate.speed_x**2 + carstate.speed_y**2 + carstate.speed_z**2)

        trackPos_SetPoint = 0.0
        speed_SetPoint = 100.0 * MPS_PER_KMH
        angle_SetPoint = 0.0

        trackPos_Diff = trackPos_SetPoint - trackPos

        trackPos_Diff_Module = math.sqrt(trackPos_Diff**2)

        trackDistance = carstate.distance_from_start

        print('')
        print('TRACK DISTANCE='+ str(trackDistance))
        print('TRACK DISTANCE='+ str(trackDistance))
        print('TRACK DISTANCE='+ str(trackDistance))
        print('')

        speed_SetPoint = 210.0
        for c in self.curves:
            start = c.startPoint()
            end = c.endPoint()
            if (trackDistance > start and trackDistance < end):
                speed_SetPoint = c.speed()
                if(self.speedSetPoint != speed_SetPoint):
                    aaaa = 3
                    #print('')
                    #print('TRACK DISTANCE=' + str(trackDistance) + ', SPEED SET POINT=' + str(speed_SetPoint))
                    #print('TRACK DISTANCE=' + str(trackDistance) + ', SPEED SET POINT=' + str(speed_SetPoint))
                    #print('TRACK DISTANCE=' + str(trackDistance) + ', SPEED SET POINT=' + str(speed_SetPoint))
                    #print('')
                break

        #speed_SetPoint = 80.0
        speed_SetPoint = speed_SetPoint * MPS_PER_KMH
        self.speedSetPoint = speed_SetPoint
        cmdDistCenter = self.pidDistCenter.calc(trackPos_SetPoint, trackPos, self.dt, distCenterKp, distCenterKd, distCenterKi)
        cmdAngle = self.pidAngle.calc(angle_SetPoint, carstate.angle, self.dt, angleKp, angleKd, angleKi)
        cmdAccelerator = self.pidSpeed.calc(speed_SetPoint, speed, self.dt, speedKp, speedKd, speedKi)

        print('cmdAngle='+str(cmdAngle))

        command.steering = -cmdAngle  + cmdDistCenter
        command.accelerator = 0.0
        command.brake = 0.0
        if(cmdAccelerator > 0.0):
            command.accelerator = cmdAccelerator
        else:
            command.brake = -cmdAccelerator

        if(command.steering > 1):
            command.steering = 1
        elif (command.steering < -1):
            command.steering = -1


        # gear shifting:
        #_logger.info('rpm, gear: {}, {}'.format(carstate.rpm, carstate.gear))
        command.gear = carstate.gear or 1
        if carstate.rpm > 7000 and carstate.gear < 6:
            #_logger.info('switching up')
            command.gear = carstate.gear + 1
        elif carstate.rpm < 2000 and carstate.gear > 1:
            #_logger.info('switching down')
            command.gear = carstate.gear - 1

        ##if self.data_logger:
         ##   self.data_logger.log(carstate, command)

        if(True == printDistance):
            _logger.info(carstate.distance_from_start)
            print(carstate.distance_from_start)

        return command
