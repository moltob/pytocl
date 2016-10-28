import logging
import math
import operator

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
    def __init__(self,breakPoint, startPoint, endPoint, speed, relativePos):
        self.bp = breakPoint
        self.sp = startPoint
        self.ep = endPoint
        self.spe = speed
        self.relPos = relativePos

    def startPoint(self):
        return self.sp

    def endPoint(self):
        return self.ep

    def speedKmh(self):
        return self.spe

    def relativePosition(self):
        return self.relPos

    def getBreakPoint(self):
        return self.bp

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
        return self.directions#-90, -75, -60, -45, -30, -20, -15, -10, -5, 0, 5, 10, 15, 20, 30, 45, 60, 75, 90

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
        #self.directions = -90, -75, -60, -45, -30, -20, -15, -10, -5, 0, 5, 10, 15, 20, 30, 45, 60, 75, 90
        self.directions = -90, -60, -40, -25, -20, -15, -10, -5, -2, 0, 2, 5, 10, 15, 20, 25, 40, 60, 90
        self.currentDriveState = DriveStateStraight(-0.8)
        self.data_logger = DataLogWriter() if logdata else None
        self.accelerator = 0.0

        self.lap = 0
        self.lastCurve = -1
        self.timeMsec = 0
        self.curves = list()
        self.speedSetPoint = 0.0

        self.currentCurveIndex = 0
        

        #c0 = Curve(100, 120,  150, 250, 0.8)
        #self.curves.append(c0)

        c1_a = Curve(360, 380, 500, 110, -0.8)
        self.curves.append(c1_a)

        #c1_b = Curve(450, 500, 80)
        #self.curves.append(c1_b)

        c2 = Curve(700, 720, 810, 110, 0.8)
        self.curves.append(c2)

        c3 = Curve(950, 980, 1100, 180, 0.8)
        self.curves.append(c3)

        c4 = Curve(1430, 1450, 1600, 160, -0.8)
        self.curves.append(c4)

        c5 = Curve(1860, 1880, 1940, 200, -0.8)
        self.curves.append(c5)

        c6pre = Curve(2300, 2320, 2380, 130, 0.8)
        self.curves.append(c6pre)

        #c6pre2 = Curve(2350, 2400, 120)
        #self.curves.append(c6pre2)

        c6 = Curve(2400, 2415, 2500, 80, -0.8)
        self.curves.append(c6)

        c7 = Curve(2600, 2650, 2800, 150, -0.8)
        self.curves.append(c7)

        c8 = Curve(2830, 2910, 3030, 165, 0.8)
        self.curves.append(c8)

        c9 = Curve(3200, 3230, 3285, 70, -0.8)
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

        if(printDistance):
            pass
            #print("DISTANCE = " + str(trackDistance))

        trackPos_SetPoint = 0.0
        angle_SetPoint = 0.0

        speed_SetPoint_kmh = 240.0
        curve = -1
        trackDistance = carstate.distance_from_start
        isInCurve = False
        for cIndex, c in enumerate(self.curves):
            curve = curve + 1
            start = c.startPoint()
            end = c.endPoint()
            breakPoint = c.getBreakPoint()
            if(trackDistance > breakPoint and trackDistance < start):
                if( self.currentDriveState.destSpeedMs != c.speedKmh()* MPS_PER_KMH):
                    self.currentDriveState.destSpeedMs = c.speedKmh() * MPS_PER_KMH
                    print("Breaking to " + str(c.speedKmh()))
            elif (trackDistance > start and trackDistance < end):
                isInCurve = True
                self.currentCurveIndex = cIndex

                if (type(self.currentDriveState) is not DriveStateCurve):
                    self.currentDriveState = DriveStateCurve(c.speedKmh() * MPS_PER_KMH, self.directions)
                    print('entered curve')

        if(not isInCurve and type(self.currentDriveState) is not DriveStateStraight):
            self.currentDriveState = DriveStateStraight(self.curves[(self.currentCurveIndex +1) % len(self.curves)].relativePosition())
            print('entered straight')

        if(curve != self.lastCurve):
            if(curve == 0):
                self.lap = self.lap + 1

        if(curve == 0 and self.lap == 1):
            speed_SetPoint_kmh = 240.0



        cmdSteering, cmdAccelerator = self.currentDriveState.drive(carstate)

        command.accelerator = 0.0
        command.brake = 0.0
        if(cmdAccelerator > 0.0):
            if(abs(carstate.distance_from_center)>1): #sind wir im Kiesbett?
                command.accelerator = 0.2
            else:
                command.accelerator = cmdAccelerator
        else:
            command.brake = -cmdAccelerator

        min_wheel_speed = 999999999
        min_wheel_speed = min(carstate.wheel_velocities)
        #print('WHEEL_SPEED=' + str(min_wheel_speed))

        if(command.brake > 0.0 and min_wheel_speed < 500):
            #pass
            print('!!!!!!! ABS')
            command.brake = 0.2

        if(command.brake == 0.0 and command.accelerator > 0.0 and command.accelerator < 1.0):
            command.accelerator = 1.0

        command.steering = cmdSteering

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

        ##if(True == printDistance):
        ##   _logger.info(carstate.distance_from_start)
        ##    print(carstate.distance_from_start)

        return command


class DriveState:
    def __init__(self):
        self.destSpeedMs = 300 * MPS_PER_KMH
        self.dt = 0.020
        self.pidSpeed = Pid()
        self.pidAngle = Pid()
        self.pidDistCenter = Pid()
        self.angle_SetPoint = 0

class DriveStateStraight(DriveState):

    def __init__(self, destOffset):
        super().__init__()
        #distCenterKp = 10.0
        self.distCenterKp = 0.3
        self.distCenterKd = 0
        self.distCenterKi = 0.0 #10.0

        self.speedKp = 15.0
        self.speedKd = 0.0
        self.speedKi = 0.0

        #angleKp = 0.07
        self.angleKp = 0.1#0.03
        self.angleKd = 0#0.01 #0.02
        self.angleKi = 0#0.0

        self.destDistanceOffset = destOffset

    def drive(self, carstate):
        #speed_SetPoint_ms = 350 * MPS_PER_KMH
        #self.speedSetPoint = speed_SetPoint_ms

        distFromCenter = carstate.distance_from_center
        speed_ms = math.sqrt(carstate.speed_x**2 + carstate.speed_y**2 + carstate.speed_z**2)
        trackDistance = carstate.distance_from_start


        cmdDistCenter = self.pidDistCenter.calc(self.destDistanceOffset, distFromCenter, self.dt, self.distCenterKp, self.distCenterKd, self.distCenterKi)
        cmdAngle = self.pidAngle.calc(self.angle_SetPoint, carstate.angle, self.dt, self.angleKp, self.angleKd, self.angleKi)
        cmdAccelerator = self.pidSpeed.calc(self.destSpeedMs, speed_ms, self.dt, self.speedKp, self.speedKd, self.speedKi)

        cmdSteering = cmdDistCenter - cmdAngle

        return cmdSteering, cmdAccelerator


class DriveStateCurve(DriveState):

    def __init__(self, destSpeedMs, directions):
        super().__init__()
        #distCenterKp = 10.0
        #self.distCenterKp = 2.5
        #self.distCenterKd = 4
        #self.distCenterKi = 0.0 #10.0

        self.speedKp = 15.0
        self.speedKd = 0.0
        self.speedKi = 0.0

        angleKp = 0.07
        self.angleKp = 0.03
        self.angleKd = 0.01 #0.02
        self.angleKi = 0.0

        self.angle_SetPoint = 0.0

        self.destSpeedMs = destSpeedMs

        self.directions = directions

    def drive(self, carstate):
        #speed_SetPoint_ms = self.speed_SetPoint_ms * MPS_PER_KMH
        #self.speedSetPoint = speed_SetPoint_ms

        distFromCenter = carstate.distance_from_center
        speed_ms = math.sqrt(carstate.speed_x**2 + carstate.speed_y**2 + carstate.speed_z**2)
        trackDistance = carstate.distance_from_start

        #Track planing:
        maxDistanceIndex, maxDistance = max(enumerate(carstate.distances_from_edge), key=operator.itemgetter(1))
        newAngle = - self.directions[maxDistanceIndex]

        #cmdDistCenter = self.pidDistCenter.calc(self.destDistanceOffset, distFromCenter, self.dt, self.distCenterKp, self.distCenterKd, self.distCenterKi)
        cmdAngle = self.pidAngle.calc(self.angle_SetPoint, newAngle, self.dt, self.angleKp, self.angleKd, self.angleKi)
        cmdAccelerator = self.pidSpeed.calc(self.destSpeedMs, speed_ms, self.dt, self.speedKp, self.speedKd, self.speedKi)

        cmdSteering = -cmdAngle



        printMaxDistanceAhead = 0
        if (printMaxDistanceAhead):
            if(maxDistance != -1):
                print('maxDistance' + str(maxDistance) + '\t angle: ' + str(newAngle))


        return cmdSteering, cmdAccelerator