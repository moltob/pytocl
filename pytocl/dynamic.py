from pytocl.car import State, Command, MPS_PER_KMH
from pytocl.lane import Lane


class Dynamic:

    def __init__ (self):
        self.speed = 0

        # out
        self.accelerator = 0
        self.gear = 0
        self.brake = 0
        self.steering = 0

        self.steerCorrection = 0

    def correctGear(self, carstate):
        self.gear = carstate.gear or 1
        if carstate.rpm > 7000 and carstate.gear < 6:
            # _logger.info('switching up')
            self.gear = carstate.gear + 1
        elif carstate.rpm < 2000 and carstate.gear > 1:
            # _logger.info('switching down')
            self.gear = carstate.gear - 1

    def simple(self, carstate, mylane: Lane):

        # dummy steering control:
        #
        speed = mylane.velocity()
        angle = mylane.angle()

        brake_high = 25
        brake_mid = 70
        brake_low = 94

        dSpeed = speed - carstate.speed_x
        self.gear = carstate.gear

        if ((speed < 0) and (speed < carstate.speed_x)):
            self.accelerator = 1
            self.gear = -1
            print("REVERSE g %f  a%  s %f" % (self.gear,self.accelerator,carstate.speed_x))
        else:
            if (self.gear == -1): self.gear = 1
            #bremsen
            if (dSpeed < 0):
                dSpeedFactor = (100/carstate.speed_x) * speed
            # hart bremsen
                if (dSpeedFactor < brake_high):
                    self.brake = 1
                    print("BRAKE HARD")
            # mittel
                elif (dSpeedFactor >= brake_high) and (dSpeedFactor < brake_mid):
                    self.brake = 0.8
                    print("BRAKE MID")
            # sanft bremsen
                elif (dSpeedFactor >= brake_mid) and (dSpeedFactor < brake_low):
                    self.brake = 0.4
                    print("BRAKE LIGHT")
                else :
                    print("BRAKE NO")
            else :
                self.brake = 0
            self.accelerate(speed, carstate)


       # print ("%f -> x %f  y %f" % (speed, carstate.speed_x, carstate.speed_y))


        # if ((carstate.distance_from_center < -0.2) or (carstate.distance_from_center > 0.2)):
        #     self.steerCorrection = 1
        #
        # if (self.steerCorrection == 1) :
        #     self.steering = (carstate.angle - carstate.distance_from_center * 0.2)
        #
        # if (carstate.distance_from_center == 0):
        #         self.steerCorrection = 0

        if (angle == 500):
            self.steering = (carstate.angle - carstate.distance_from_center * 0.2)
        else:
            self.steering = (-1)*angle/77



       # self.accelerator = min(1, self.accelerator)
       # self.accelerator = max(-1, self.accelerator)

        # _logger.info('accelerator: {}'.format(command.accelerator))

        # gear shifting:
        #_logger.info('rpm, gear: {}, {}'.format(carstate.rpm, carstate.gear))


        if carstate.rpm > 8000 and carstate.gear < 6:
            # _logger.info('switching up')
            self.gear = carstate.gear + 1
        elif carstate.rpm < 2700 and carstate.gear > 1:
            #_logger.info('switching down')
            self.gear = carstate.gear -1

    def accelerate(self, speed, carstate : State):
        if carstate.distance_from_start < 100 or carstate.distance_from_start > 3580:
            self.accelerator = 1
            #print("Dist: " + str(carstate.distance_from_start))
        elif (speed > carstate.speed_x):
            if abs(carstate.speed_y) > carstate.speed_x+10:
                self.accelerator = -0.5
            elif abs(carstate.speed_y) > carstate.speed_x+5:
                self.accelerator = 0
            else:
                if self.accelerator < 0.5:
                    self.accelerator = 0.5
                else:
                    self.accelerator = 1
        else:
            self.accelerator = 0

        #print( "acc: " + str(self.accelerator))

