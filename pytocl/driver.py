import logging

from pytocl.analysis import DataLogWriter
from pytocl.car import State, Command, MPS_PER_KMH, KMH_PER_MPS, G_CONST

_logger = logging.getLogger(__name__)


class Driver:
    """Driving logic.

    Implement the driving intelligence in this class by processing the current car state as inputs
    creating car control commands as a response. The ``drive`` function is called periodically
    every 20ms and must return a command within 10ms wall time.
    """

    CURVE_DETECTION_THRESHOLD = 50

    def __init__(self, logdata=True):
        self.data_logger = DataLogWriter() if logdata else None
        self.accelerator = 0.0
        self.breaking = 0.0
        self.currentAngleCorr = 0.0
        self.carstate_old = None
        self.angle_diff_quotient = 0.0
        self.target_velocity = 50
        self.prev_dist_from_edge_mitte = 0.0
        self.brake_begin = False
        self.brake_begin_consumed = False
        self.outside_track = False

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

    def select_gear(self, carstate: State, command: Command):

        # gear shifting:
        #_logger.info('rpm, gear: {}, {}'.format(carstate.rpm, carstate.gear))
        command.gear = carstate.gear or 1
        if carstate.rpm > 9500 and carstate.gear < 6:
            #_logger.info('switching up')
            command.gear = carstate.gear + 1
        elif carstate.rpm < 4000 and carstate.gear > 2:
            #_logger.info('switching down')
            command.gear = carstate.gear - 1
        elif carstate.rpm < 3000 and carstate.gear > 1:
            #_logger.info('switching down')
            command.gear = carstate.gear - 1

    def getTrajectoryOfOpponent(self, distance, angle) -> float :
        import math
        xDistance = math.cos(angle) * distance
        return xDistance

    def control_steering_angle (self, carstate: State, command: Command):

        if self.outside_track == False:
            # korrektur zum aktuellen Winkel
            self.currentAngleCorr = (carstate.angle / 21)

            # korrektur zum zentrum
            if (carstate.distance_from_center > 0.1  and carstate.distance_from_center <= 1):
                self.currentAngleCorr -= 0.2
            elif (carstate.distance_from_center < -0.1 and carstate.distance_from_center >= -1):
                self.currentAngleCorr += 0.2

            dist_left = (carstate.distances_from_edge[6] + carstate.distances_from_edge[7] + carstate.distances_from_edge[8])/3
            dist_right = (carstate.distances_from_edge[10] + carstate.distances_from_edge[11] + carstate.distances_from_edge[12])/3
            dist_centre = carstate.distances_from_edge[9]

            if (dist_centre > dist_left and dist_centre > dist_right):
                self.currentAngleCorr += 0.0
            # elif (dist_left > dist_centre and dist_centre > dist_right):
            #     # left turn ahead
            #     self.currentAngleCorr += 0.15
            # elif (dist_left < dist_centre and dist_centre < dist_right):
            #     # right turn ahead
            #     self.currentAngleCorr -= 0.15
            elif (dist_left > dist_right):
                self.currentAngleCorr += 0.2
            else:
                self.currentAngleCorr -= 0.2

            # normalize to range
            if (self.currentAngleCorr < -1.0):
                self.currentAngleCorr = -1.0
            elif (self.currentAngleCorr > 1.0):
                self.currentAngleCorr = 1.0

            command.steering = self.currentAngleCorr


    def control_target_velocity (self, carstate: State):


        dist_from_edge_mitte = (carstate.distances_from_edge[7] +
                                carstate.distances_from_edge[8] +
                                carstate.distances_from_edge[9] +
                                carstate.distances_from_edge[10] +
                                carstate.distances_from_edge[11]) / 5

            #print("dist edge mitte" + str(dist_from_edge_mitte))

        if self.outside_track == False:
            #        self.target_velocity = carstate.speed_x * KMH_PER_MPS
            current_velocity_kmh =  carstate.speed_x * KMH_PER_MPS

            if (dist_from_edge_mitte < self.CURVE_DETECTION_THRESHOLD * (current_velocity_kmh / 150)):

                print(carstate.speed_y*KMH_PER_MPS)

                # if leaving turn
                if (self.prev_dist_from_edge_mitte < dist_from_edge_mitte):
                        self.target_velocity += (18 -(abs(carstate.speed_y)*KMH_PER_MPS*2))

                else:
                    if (self.brake_begin_consumed == False) :
                        self.target_velocity = current_velocity_kmh - 20
                        self.brake_begin_consumed = True
                    else:
                        self.target_velocity -= 10

            elif dist_from_edge_mitte >= self.CURVE_DETECTION_THRESHOLD:
                self.brake_begin_consumed = False
                self.target_velocity = 250

            if self.target_velocity < 70:
                self.target_velocity = 70;

        else:
            self.target_velocity = 30

        self.prev_dist_from_edge_mitte = dist_from_edge_mitte


    def control_opponents_backwards (self, carstate: State, command: Command):

        if self.outside_track == False:
            for i in [0, 1, 2, 3, 4, 5, 6, 30, 31, 32, 33, 34, 35]:
                if (carstate.opponents[i] < 190):
                    print (str(i) + ": "+ str(carstate.opponents[i]))

            opponent_detection_left = 0
            opponent_detection_right = 0

            for i in [0, 1, 2, 3, 4, 5, 6, 7, 8]:
                if ((carstate.opponents[i] < 20) and ((opponent_detection_left > carstate.opponents[i])) or (opponent_detection_left == 0)):
                    opponent_detection_left = carstate.opponents[i]

            for i in [28, 29, 30, 31, 32, 33, 34, 35]:
                if ((carstate.opponents[i] < 20) and ((opponent_detection_right > carstate.opponents[i]))or (opponent_detection_right == 0)):
                    opponent_detection_right = carstate.opponents[i]

            if (opponent_detection_left < 20 or  opponent_detection_right < 20):

                if (opponent_detection_left > opponent_detection_right):
                    command.steering -= 0.3
                    command.steering = max(-1, command.steering)
                    print("RIGHT")
                else:
                    command.steering += 0.3
                    command.steering = min (1, command.steering)
                    print ("LEFT")


    def overtake_opponent (self, carstate: State, command: Command):

        opponent_detection_front = -1
        opponent_detection_left = 0
        opponent_detection_right = 0

        #is opponent in front of us
        for i in [16, 17, 18]:
            print (str(i) + ":" + str(carstate.opponents[i]))
            if ( (carstate.opponents[i] < 30) and ((opponent_detection_front > carstate.opponents[i]) or (opponent_detection_front < 0)) ):
                opponent_detection_front = carstate.opponents[i]

        for i in [12, 13, 14, 15]:
            if ((opponent_detection_left > carstate.opponents[i]) or (opponent_detection_left == 0)):
                opponent_detection_left = carstate.opponents[i]

        for i in [19, 20, 21, 22]:
            if ((opponent_detection_right > carstate.opponents[i]) or (opponent_detection_right == 0) ):
                opponent_detection_right = carstate.opponents[i]

        print (opponent_detection_front)
        print (opponent_detection_left)
        print (opponent_detection_right)


        if (opponent_detection_front > -1 and (opponent_detection_left > opponent_detection_front or opponent_detection_right > opponent_detection_front)):

            print ("opponent detected")

            if (opponent_detection_left > opponent_detection_right):
                command.steering += 0.45
                command.steering = min(1, command.steering)
                print("LEFT")
            else:
                command.steering -= 0.45
                command.steering = max(-1, command.steering)
                print("RIGHT")

    def select_steering(self, carstate: State, command: Command):

        self.checkOutsideTrack(carstate, command)
        self.control_steering_angle(carstate, command)
        self.control_target_velocity(carstate)
        self.control_opponents_backwards (carstate, command)
        self.overtake_opponent(carstate, command)

    def checkOutsideTrack(self, carstate: State, command: Command):
        self.outside_track = False

        #prev_angle_corr = self.currentAngleCorr
        self.currentAngleCorr = (carstate.angle / 21)

        # korrektur weil ausserhalb der strecke
        if (carstate.distance_from_center > 1):
            # left outside
            self.outside_track = True
            if (carstate.angle >= 90):
                self.currentAngleCorr = 1
            else:
                self.currentAngleCorr = -1
        elif (carstate.distance_from_center < -1):
            # right outside
            self.outside_track = True
            if (carstate.angle <= -90):
                self.currentAngleCorr = -1
            else:
                self.currentAngleCorr = 1

        if (self.currentAngleCorr < -1.0):
            self.currentAngleCorr = -1.0
        elif (self.currentAngleCorr > 1.0):
            self.currentAngleCorr = 1.0

        command.steering = self.currentAngleCorr


    def select_acceleration(self, carstate: State, command: Command):

        if carstate.speed_x < self.target_velocity * MPS_PER_KMH:
            self.accelerator += 0.2
        else:
            self.accelerator = 0

        # if self.target_velocity * MPS_PER_KMH < carstate.speed_x:
        #     if (carstate.speed_x - self.target_velocity * MPS_PER_KMH) < 5:
        #         self.breaking = 0.0
        #     elif (carstate.speed_x * KMH_PER_MPS - self.target_velocity ) >= 40:
        #         if self.breaking > 0.0:
        #             self.breaking += 0.02
        #         else:
        #             if (carstate.speed_x*KMH_PER_MPS > 150):
        #                 self.breaking = 0.60
        #             else:
        #                 self.breaking = 0.20
        # else:
        #     self.breaking = 0.0
        #
        self.accelerator = min(1, self.accelerator)
        self.accelerator = max(-1, self.accelerator)
        #
        # self.breaking = min(1, self.breaking)
        #
        command.accelerator = self.accelerator
        # command.brake = self.breaking
        #
        # #if (command.brake > 0.0):
        # #_logger.info('accelerator: {}'.format(command.accelerator))
        # #_logger.info('break: {}'.format(self.breaking))
        # _logger.info('target velocity: {}'.format(self.target_velocity))
        # _logger.info('current speed: {}'.format(carstate.speed_x * KMH_PER_MPS))

    def select_brake(self, carstate: State, command: Command):
        if (carstate.speed_x - self.target_velocity * MPS_PER_KMH) < 5:
            self.breaking = 0.0
        else:
            current_speed_sqr_mps = carstate.speed_x * carstate.speed_x
            allowed_speed = self.target_velocity
            look_ahead_dist_meter = self.prev_dist_from_edge_mitte

            allowed_speed_sqr_mps = (allowed_speed * MPS_PER_KMH) * (allowed_speed * MPS_PER_KMH)

            #(currentspeedsqr - allowedspeedsqr) / (2.0 * mu * G);
            brake_dist_meter = (current_speed_sqr_mps - allowed_speed_sqr_mps) / (2*G_CONST)

            _logger.info('brake dist: {}'.format(brake_dist_meter))
            _logger.info('look_ahead_dist: {}'.format(look_ahead_dist_meter))

            if brake_dist_meter > look_ahead_dist_meter:
                self.breaking = 0.7

            self.breaking = min(1, self.breaking)
            command.brake = self.breaking


    def drive(self, carstate: State) -> Command:
        """Produces driving command in response to newly received car state.

        This is a dummy driving routine, very dumb and not really considering a lot of inputs. But
        it will get the car (if not disturbed by other drivers) successfully driven along the race
        track.
        """
        if (self.carstate_old == None):
            self.carstate_old = carstate
            self.carstate_old.angle = 0.0

        command = Command()

        # steering control:
        self.select_steering(carstate, command)

        # basic acceleration to target speed:
        self.select_acceleration(carstate, command)

        self.select_brake(carstate, command)

        self.select_gear(carstate, command)

        if self.data_logger:
            self.data_logger.log(carstate, command)

        self.angle_old = carstate.angle

        self.carstate_old = carstate

        return command
