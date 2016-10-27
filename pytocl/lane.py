class Lane:




    def __init__ (self):
        self.velocity = 120
        pass

    def lookfwd(self, carstate):
        max_dist = 0
        max_idx = -1
        for i in range(0,19):
            if carstate.distances_from_edge[i] > max_dist:
                max_dist = carstate.distances_from_edge[i]
                max_idx = i





    def velocity(self):
        return self.velocity

    def angle(self):
        return 0


#_logger.info('distance_from_center: {}'.format(carstate.distance_from_center))
#_logger.info('distance_from_edge: {}'.format(carstate.distances_from_edge))
#_logger.info('angle: {}'.format(carstate.angle))