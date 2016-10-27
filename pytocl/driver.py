import logging

from pytocl.analysis import DataLogWriter
from pytocl.car import State, Command, MPS_PER_KMH

_logger = logging.getLogger(__name__)


class Driver:
    """Driving logic.

    Implement the driving intelligence in this class by processing the current car state as inputs
    creating car control commands as a response. The ``drive`` function is called periodically
    every 20ms and must return a command within 10ms wall time.
    """

    def __init__(self, logdata=True):
        self.data_logger = DataLogWriter() if logdata else None
        self.accelerator = 0.0
        self.breaking = 0.0
        self.currentAngleCorr = 0.0
        self.carstate_old = None
        self.angle_diff_quotient = 0.0
        self.target_velocity = 50
        self.prev_dist_from_edge_mitte = 0.0

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
        if carstate.rpm > 7000 and carstate.gear < 6:
            _logger.info('switching up')
            command.gear = carstate.gear + 1
        elif carstate.rpm < 2000 and carstate.gear > 1:
            _logger.info('switching down')
            command.gear = carstate.gear - 1

    def select_steering(self, carstate: State, command: Command):
        #command.steering = (carstate.angle - carstate.distance_from_center * 0.5)


        # first drive parallel to tangente
        # if distance from center more than 0.1 normalized
        #   correct against center
        # if angle_diversion increasing - reduce speed in steps of 5%
        # else if decreasing - increase speed
        # else reach max of 120

#         #steering_angle_correction = carstate.angle
# #        self.currentAngleCorr = (carstate.angle/21 + self.currentAngleCorr)/2
#         if (abs(self.carstate_old.angle) > 0.0):
#             curr_angle_diff_quotient = abs(self.carstate_old.angle - carstate.angle) / abs(self.carstate_old.angle)
#         else:
#             curr_angle_diff_quotient = 0.0
#
#         if curr_angle_diff_quotient < 0.01 :
#             self.target_velocity = 140
#         else:
#             if (self.angle_diff_quotient < curr_angle_diff_quotient*0.8 ) :
#                 self.target_velocity -=20
#             else:
#                 self.target_velocity = 140
#
#         # if self.target_velocity < 120:
#         #     print("old angle diff quotient " + str(self.angle_diff_quotient))
#         #     print("curr angle diff quotient " + str(curr_angle_diff_quotient))
#         #     print("target velocity " + str(self.target_velocity))
#         #     print("-----------------------")
#
#         self.angle_diff_quotient = curr_angle_diff_quotient


        self.currentAngleCorr = 1.0*(carstate.angle / 21) + 0.0*(self.currentAngleCorr)

        # # korrektur wegen zu hohem angle
        # if (abs(carstate.angle) < 2):
        #     pass
        # elif (self.carstate_old.angle < carstate.angle and self.currentAngleCorr < 1):
        #     self.currentAngleCorr = self.currentAngleCorr + 0.1#*(angle_diff_quat)
        # elif (self.angle_old > carstate.angle and self.currentAngleCorr > -1):
        #     self.currentAngleCorr = self.currentAngleCorr - 0.1#*(angle_diff_quat)


        # korrektur zum zentrum
        if (carstate.distance_from_center > 0.1  and self.currentAngleCorr < 1):
            self.currentAngleCorr -= 0.2
        elif (carstate.distance_from_center < -0.1 and self.currentAngleCorr > -1):
            self.currentAngleCorr += 0.2


        # print (self.carstate_old.angle)
        # print (carstate.angle)
        # print (self.currentAngleCorr)
        # print ("-----------------------")


        dist_from_edge_mitte = (carstate.distances_from_edge[7]+
                                carstate.distances_from_edge[8] +
                                carstate.distances_from_edge[9] +
                                carstate.distances_from_edge[10] +
                                carstate.distances_from_edge[11]) / 5

        #dist_from_edge_mitte = carstate.distances_from_edge[9]
        print("dist edge mitte" + str(dist_from_edge_mitte))
        # if (dist_from_edge_mitte < 50):
        #     self.target_velocity -= 15
        # elif (dist_from_edge_mitte < 20):
        #     if (self.prev_dist_from_edge_mitte > dist_from_edge_mitte):
        #         self.target_velocity -= 25
        #     else:
        #         self.target_velocity += 15
        # elif (dist_from_edge_mitte > 50):
        #     self.target_velocity = 180

        if (dist_from_edge_mitte < 55):
            #if leaving turn
            if (self.prev_dist_from_edge_mitte < dist_from_edge_mitte):
                self.target_velocity += 15
            else:
                self.target_velocity -= 25
        elif dist_from_edge_mitte >= 55:
            self.target_velocity = 190

        if self.target_velocity < 60:
            self.target_velocity = 60;

        self.prev_dist_from_edge_mitte = dist_from_edge_mitte

        # if abs(self.currentAngleCorr) > 0.06:
        #     self.target_velocity -= 25
        #
        #     if self.target_velocity < 40:
        #         self.target_velocity = 40;
        # else:
        #     self.target_velocity = 120
        #
        # print(self.target_velocity)
        # print(self.currentAngleCorr)

        # command.steering = (carstate.angle*self.currentAngleCorr);
        command.steering = self.currentAngleCorr

    def select_acceleration(self, carstate: State, command: Command):
        # if carstate.speed_x < 80 * MPS_PER_KMH:
        #     self.accelerator += 0.1
        # else:
        #     self.accelerator = 0

        if carstate.speed_x < self.target_velocity * MPS_PER_KMH:
            self.accelerator += 0.1
        else:
            self.accelerator = 0

        if self.target_velocity * MPS_PER_KMH < carstate.speed_x:
            if (carstate.speed_x - self.target_velocity * MPS_PER_KMH ) > 20:
                if self.breaking > 0.0:
                    self.breaking += 0.1
                else:
                    self.breaking = 0.6
        else:
            self.breaking = 0.0

        self.accelerator = min(1, self.accelerator)
        self.accelerator = max(-1, self.accelerator)

        self.breaking = min(1, self.breaking)

        command.accelerator = self.accelerator
        command.brake = self.breaking

        #if (command.brake > 0.0):
        _logger.info('accelerator: {}'.format(command.accelerator))
        _logger.info('break: {}'.format(self.breaking))
        # _logger.info('target velocity: {}'.format(self.target_velocity))
        # _logger.info('current speed: {}'.format(carstate.speed_x))

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

        self.select_gear(carstate, command)

        if self.data_logger:
            self.data_logger.log(carstate, command)

        self.angle_old = carstate.angle

        self.carstate_old = carstate

        return command
