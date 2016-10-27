from pytocl.car import State, Command, MPS_PER_KMH

class Dynamic:

    def __init__ (self):
        self.speed = 0

        # out
        self.acceleration = 0
        self.gear = 0
        self.brake = 0
        self.steering = 0

    def simple(self, carstate):

        # dummy steering control:
         self.steering = (carstate.angle - carstate.distance_from_center * 0.1)

        # basic acceleration to target speed:
         if carstate.speed_x <30 * MPS_PER_KMH:
             self.accelerator += 0.1
         else:
             self.accelerator = 0
         self.accelerator = min(1, self.accelerator)
         self.accelerator = max(-1, self.accelerator)

        # _logger.info('accelerator: {}'.format(command.accelerator))

         # gear shifting:
         #_logger.info('rpm, gear: {}, {}'.format(carstate.rpm, carstate.gear))
         gear = carstate.gear or 1
         if carstate.rpm > 7000 and carstate.gear < 6:
            # _logger.info('switching up')
             gear = carstate.gear + 1
         elif carstate.rpm < 2000 and carstate.gear > 1:
             #_logger.info('switching down')
             gear = carstate.gear - 1