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

        if (speed < carstate.speed_x):
            self.brake = 0.6
        else : self.brake = 0

        if (speed > carstate.speed_x):
            if ((carstate.speed_x < carstate.speed_y) or (carstate.speed_y<5)):
                self.accelerator += 0.8
        else:
            self.accelerator -= 0.35


        print ("%f -> x %f  y %f" % (speed, carstate.speed_x, carstate.speed_y))


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
            self.steering = (-1)*angle/90



       # self.accelerator = min(1, self.accelerator)
       # self.accelerator = max(-1, self.accelerator)

        # _logger.info('accelerator: {}'.format(command.accelerator))

        # gear shifting:
        #_logger.info('rpm, gear: {}, {}'.format(carstate.rpm, carstate.gear))

        self.gear = carstate.gear or 1
        if carstate.rpm > 7000 and carstate.gear < 6:
            # _logger.info('switching up')
            self.gear = carstate.gear + 1
        elif carstate.rpm < 2000 and carstate.gear > 1:
            #_logger.info('switching down')
            self.gear = carstate.gear - 1