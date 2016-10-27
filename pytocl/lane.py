from pytocl.analysis import DataLogWriter

angles = [-90, -75, -60, -45, -30, -20, -15, -10, -5, 0, 5, 10, 15, 20, 30, 45, 60, 75, 90]

class Lane:
    last_ang = -1
    
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

    def new_ang(self, angle):
        print (Lane.last_ang)
        print(angle)
        diff = 0
        new_angle = angle
        if angle >= 0 and Lane.last_ang>=0:
            return angle
        if angle<=0 and Lane.last_ang<=0:
            return angle

        diff = angle - Lane.last_ang

        if abs(diff) >= 10:
            if diff >= 0:
                new_angle= Lane.last_ang+10
            else:
                new_angle = Lane.last_ang - 10
            print (str(diff) + "   *****************************************************************")
        else:
            new_angle=angle
        return new_angle

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

        if max_dist>150:
            self.vel = max_dist * 250 / 200
        elif max_dist > 90:
            self.vel = max_dist
        elif max_dist > 50:
            self.vel = max_dist * 0.6
        else:
            self.vel = max_dist * 0.4



            #print (carstate.distances_from_edge)
            #self.vel=10

        #print(carstate.distances_from_edge)
        #self.ang = self.new_ang(angles[max_idx])
        self.ang = angles[max_idx]
        #Lane.last_ang = self.ang
        if carstate.distance_from_start >2400 and carstate.distance_from_start <2499:
            self.vel=10
            print(' #############   Winkel ' +  str(self.ang) + '    ####################')

        print('velocity, angle : {}, {}, {}, {}'.format(max_dist, self.vel, self.ang, carstate.distance_from_start))
     #   print('distance_from_edge: {}'.format(carstate.distances_from_edge))

    def velocity(self):
        return self.vel

    def angle(self):
        return self.ang


#_logger.info('distance_from_center: {}'.format(carstate.distance_from_center))
#_logger.info('distance_from_edge: {}'.format(carstate.distances_from_edge))
#_logger.info('angle: {}'.format(carstate.angle))