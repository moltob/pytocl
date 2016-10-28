from pytocl.pid import PID
from pytocl.car import State

CENTER = 0
LEFT = -1
RIGHT = 1


class Orientation:
    def __init__(self, position, side):
        self.position = position
        self.side = side

class Steering:

    def __init__(self):
        self.control = PID(0.7, 0.05, 0, Integrator_max=1, Integrator_min=-1)
        self.track_position = CENTER
        self.orientation = [Orientation(0, LEFT),
                            Orientation(500, RIGHT), Orientation(1270, LEFT),
                            Orientation(2200, RIGHT),
                            Orientation(2400,CENTER),
                            Orientation(2600, LEFT),
                            Orientation(2800, RIGHT),
                            Orientation(3300, CENTER),
                            Orientation(3100, LEFT)]
        # self.control = PID(1, 0, 0)

    def select_track_position(self, carstate: State):
        self.track_position = CENTER
        for info in self.orientation:
            if carstate.distance_from_start >= info.position:
                self.track_position = info.side

    def update(self, carstate: State):
        self.select_track_position(carstate)
        if carstate.distances_from_egde_valid:
            if self.track_position == LEFT:
                distance_error = 1.5 - carstate.distances_from_edge[0]
            elif self.track_position == RIGHT:
                distance_error = -1.5 + carstate.distances_from_edge[18]
            else:
                distance_error = carstate.distance_from_center * 8
        else:
            distance_error = carstate.distance_from_center * 4

        deltaAngle = max(min(0.8, (carstate.angle / 10.0) - distance_error * 0.1), -0.8)
        return self.control.update(deltaAngle)

# import math
# math.radiand(grad)
# math.cos(math.radiand(grad))
# winkel + entfernung auf abstand: length * math.cos(math.radiand(winkel))
