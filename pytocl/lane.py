from pytocl.analysis import DataLogWriter

angles = [-90, -75, -60, -45, -30, -20, -15, -10, -5, 0, 5, 10, 15, 20, 30, 45, 60, 75, 90]

class Lane:

    last_dist_from_start = -1
    backwards = False
    backcnt = 0
    
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
        #print ('**********************************************************************************************************')
        max_dist = 0
        max_idx = -1

        if carstate.distances_from_edge[0] == -1 and carstate.distances_from_edge[18] == -1 and carstate.distances_from_edge[9] == -1:
            print('***************')
            if carstate.speed_x < 10 \
                    and (carstate.distance_from_center < 0 and 10 < carstate.angle < 170) \
                    and (carstate.distance_from_center > 0 and -10 > carstate.angle > -170):
                Lane.backwards = True
                print('Set to backwards to True')


            print('distance_from_edge: {}'.format(carstate.distances_from_edge))
            self.vel = 10
            print('==> ' + str(carstate.distance_from_center) + ' --- ' + str(carstate.angle)+ ' --- ' + str(carstate.speed_x))
            #print (carstate.distances_from_edge)
            print(str(carstate.distance_from_center) + ' --- ' + str(carstate.angle))
            if carstate.distance_from_center < 0:
                self.ang = -30 - carstate.angle
            else:
                self.ang = 30 - carstate.angle

            if Lane.backwards == True:
                self.vel = -10

            #print('Direction: ' + str(Lane.backwards))
            print (self.vel)
            print (self.ang)
            return
        #else:
            #print('*==> ' + str(carstate.distance_from_center) + ' --- ' + str(carstate.angle) + ' --- ' + str(carstate.distance_from_start))

        if carstate.distance_from_start > 30 and carstate.distance_from_start < Lane.last_dist_from_start:
            self.vel = 10
            print(' BACKWARDS ***************')
            print('==> ' + str(carstate.distance_from_start) + ' --- ' + str(Lane.last_dist_from_start) + ' --- ' + str(
                carstate.speed_x))
            # print (carstate.distances_from_edge)
            # print(str(carstate.distance_from_center) + ' --- ' + str(carstate.angle))
            if carstate.distance_from_center < 0:
                self.ang = -30 - carstate.angle
            else:
                self.ang = 30 - carstate.angle

            print(self.vel)
            print(self.ang)
            return

        Lane.last_dist_from_start = carstate.distance_from_start



        Lane.backwards = False

        for i in range(0,19):
            if carstate.distances_from_edge[i] > max_dist:
                max_dist = carstate.distances_from_edge[i]
                max_idx = i

        if max_dist>150:
            self.vel = max_dist * 500 / 200
        elif max_dist > 90:
            self.vel = max_dist
        elif max_dist > 50:
            self.vel = max_dist * 0.6
        else:
            self.vel = max_dist * max_dist / 100

        self.ang = angles[max_idx]
        #Lane.last_ang = self.ang

        #if carstate.distance_from_start >2400 and carstate.distance_from_start <2499:
            #self.vel=10
            #print(' #############   Winkel ' +  str(self.ang) + '    ####################')

        #print('velocity, angle : {}, {}, {}, {}'.format(max_dist, self.vel, self.ang, carstate.distance_from_start))
        #print('distance_from_edge: {}'.format(carstate.distances_from_edge))

    def velocity(self):
        return self.vel

    def angle(self):
        return self.ang


#_logger.info('distance_from_center: {}'.format(carstate.distance_from_center))
#_logger.info('distance_from_edge: {}'.format(carstate.distances_from_edge))
#_logger.info('angle: {}'.format(carstate.angle))