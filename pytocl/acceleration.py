from pytocl.pid import PID
from pytocl.car import State, MPS_PER_KMH

class TrackParameter:
    def __init__(self, start, velocity):
        self.start = start
        self.velocity = velocity

class Acceleration:
    def __init__(self):
        self.control = PID(0.5, 0.1, 0.2, Integrator_max=20, Integrator_min=-20)
        self.targetVelocity = 21.6
        self.targetTrackVelocity = [
            TrackParameter(350, 15), TrackParameter(400+100, 30),
            TrackParameter(2350, 15), TrackParameter(2500, 35),
            TrackParameter(3200, 15), TrackParameter(3300, 60)]

    def setTargetVelocity(self, carstate):
        self.targetVelocity = 40
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
