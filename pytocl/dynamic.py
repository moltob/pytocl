from pytocl.car import State, Command, MPS_PER_KMH

class Dynamic:

    def __init__ (self):
        self.speed = 0

        # out
        self.accelerator = 0
        self.gear = 0
        self.brake = 0
        self.steering = 0

    def correctGear(self, carstate):
        self.gear = carstate.gear or 1
        if carstate.rpm > 7000 and carstate.gear < 6:
            # _logger.info('switching up')
            self.gear = carstate.gear + 1
        elif carstate.rpm < 2000 and carstate.gear > 1:
            # _logger.info('switching down')
            self.gear = carstate.gear - 1

    def simple(self, carstate, lane):

        # dummy steering control:
         if ((carstate.distance_from_center < -0.5) or (carstate.distance_from_center > 0.5)):
             self.steering = (carstate.angle - carstate.distance_from_center * 0.5)

        speed = lane.velocity;
        angle = lane.angle();


        # basic acceleration to target speed:
         if carstate.speed_x <50 * MPS_PER_KMH:
             self.accelerator += 0.1
         else:
             self.accelerator = 0
         self.accelerator = min(1, self.accelerator)
         self.accelerator = max(-1, self.accelerator)

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