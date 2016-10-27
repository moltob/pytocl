from pytocl.car import State
from .Coordinate import Coordinate
import math

class TrajectoryPlanner:
    def __init__(self):
        self.rangeFinderAngles = [-90, -75, -60, -45, -30, -20, -15, -10, -5, 0, 5, 10, 15, 20, 30, 45, 60, 75, 90]
    @property
    def range_finder_angles(self):
        """Iterable of 19 fixed range finder directions [deg].

        The values are used once at startup of the client to set the directions of range finders.
        During regular execution, a 19-valued vector of track distances in these directions is
        returned in ``state.State.tracks``.
        """
        return -90, -75, -60, -45, -30, -20, -15, -10, -5, 0, 5, 10, 15, 20, 30, 45, 60, 75, 90

    def update(self, carstate: State) -> Coordinate:

        trackLimitCoordinatesX = []
        trackLimitCoordinatesY = []

        for index,measurement in enumerate(carstate.distances_from_edge):
            if measurement > -1:
                trackLimitCoordinatesX.append(measurement * math.cos(self.rangeFinderAngles[index]/360))
                trackLimitCoordinatesY.append(measurement * math.sin(self.rangeFinderAngles[index]/360))

        leftTrackBorderX = 0
        leftTrackBorderY = 0
        rightTrackBorderX = 0
        rightTrackBorderY = 0
        for x, y in zip(trackLimitCoordinatesX, trackLimitCoordinatesY):
            if x > leftTrackBorderX and y > leftTrackBorderY:
                leftTrackBorderX = x
                leftTrackBorderY = y

            if x > leftTrackBorderX and y < leftTrackBorderY:
                rightTrackBorderX = x
                rightTrackBorderY = y

        targetX = min(rightTrackBorderX, leftTrackBorderX) + math.fabs(leftTrackBorderX - rightTrackBorderX)/2
        targetY = (leftTrackBorderY + rightTrackBorderY)/2

        distance = math.sqrt(targetX*targetX + targetY*targetY)

        if(targetX > 0):
            angle = math.atan(targetY/targetX)*180/math.pi
        else:
            angle = 0

        return Coordinate(distance, angle)