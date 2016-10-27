from pytocl.analysis import DataLogWriter

angles = [-90, -75, -60, -45, -30, -20, -15, -10, -5, 0, 5, 10, 15, 20, 30, 45, 60, 75, 90]

class Lane:

    def __init__ (self):
        self.vel = 0
        self.ang = -1
        self.data_logger = DataLogWriter()


    @property
    def range_finder_angles(self):
        """Iterable of 19 fixed range finder directions [deg].

        The values are used once at startup of the client to set the directions of range finders.
        During regular execution, a 19-valued vector of track distances in these directions is
        returned in ``state.State.tracks``.
        """
        return -90, -75, -60, -45, -30, -20, -15, -10, -5, 0, 5, 10, 15, 20, 30, 45, 60, 75, 90

    def lookfwd(self, carstate):
        max_dist = 0
        max_idx = -1
        if carstate.distances_from_edge[0] == -1 and carstate.distances_from_edge[18] == -1 and carstate.distances_from_edge[9] == -1:
            self.vel = 40
            self.ang = 500
            return


        for i in range(0,19):
            if carstate.distances_from_edge[i] > max_dist:
                max_dist = carstate.distances_from_edge[i]
                max_idx = i

        if (max_dist<80):
            self.vel = max_dist * 0.6
        else: self.vel = max_dist
        if carstate.distance_from_start >2440 and carstate.distance_from_start <2550:
            self.vel=10
        self.ang = angles[max_idx]


        print('velocity, angle : {}, {}, {}'.format(self.vel, self.ang, carstate.distance_from_start))
     #   print('distance_from_edge: {}'.format(carstate.distances_from_edge))

    def velocity(self):
        return self.vel

    def angle(self):
        return self.ang


#_logger.info('distance_from_center: {}'.format(carstate.distance_from_center))
#_logger.info('distance_from_edge: {}'.format(carstate.distances_from_edge))
#_logger.info('angle: {}'.format(carstate.angle))