from pytocl.pid import PID
from pytocl.car import State, MPS_PER_KMH

MAX_VELOCITY_MS = 250.0/3.6

class TrackParameter:
    def __init__(self, start, velocity):
        self.start = start
        self.velocity = velocity

class Acceleration:
    def __init__(self):
        self.control = PID(0.4, 0.0, 0.1, Integrator_max=20, Integrator_min=-20)
        self.targetVelocity = 22
        self.targetTrackVelocity = [
            TrackParameter(0, MAX_VELOCITY_MS),
            TrackParameter(160, 65), TrackParameter(180, MAX_VELOCITY_MS),
            TrackParameter(360, 23), TrackParameter(450, 24),
            TrackParameter(500, MAX_VELOCITY_MS),
            TrackParameter(700, 28), TrackParameter(750, MAX_VELOCITY_MS),
            TrackParameter(970, 35), TrackParameter(1000, MAX_VELOCITY_MS),
            TrackParameter(1440, 30), TrackParameter(1500, MAX_VELOCITY_MS),
            TrackParameter(1870, 33), TrackParameter(1930, MAX_VELOCITY_MS),
            #Schikane
            TrackParameter(2320, 45), TrackParameter(2330, 38),
            TrackParameter(2410, 20), TrackParameter(2490, 28),
            TrackParameter(2520, 36),
            TrackParameter(2590, 36), TrackParameter(2670, MAX_VELOCITY_MS),
            TrackParameter(2920, 35), TrackParameter(2980, MAX_VELOCITY_MS),
            TrackParameter(3200, 22),
            TrackParameter(3225, 15), TrackParameter(3270, MAX_VELOCITY_MS)]

    def setTargetVelocity(self, carstate):
        self.targetVelocity = MAX_VELOCITY_MS
        position = carstate.distance_from_start
        for track in self.targetTrackVelocity:
            if position >= track.start:
                self.targetVelocity = track.velocity

    def update(self, carstate):
        #deltaAngle = max(min(1, (carstate.angle / 10.0) - (carstate.distance_from_center * 0.4)), -1)

        #self.targetVelocity = max(20, ((1.0 - abs(deltaAngle)) * 30.0))

        self.setTargetVelocity(carstate)
        deltaVelocity = (self.targetVelocity - (carstate.speed_x))

        return self.control.update(deltaVelocity)
