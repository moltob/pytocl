from pytocl.car import State
from .Coordinate import Coordinate
import math

class TrajectoryPlanner:
    def __init__(self):
        self.rangeFinderAngles = [-90, -75, -60, -45, -30, -20, -15, -10, -5, 0, 5, 10, 15, 20, 30, 45, 60, 75, 90]
        self.anglesAverage = [0]*1
        self.leftCurveAverage = [0] * 5
        self.rightCurveAverage = [0] * 5
        self.NULL_INDEX = 9

    @property
    def range_finder_angles(self):
        """Iterable of 19 fixed range finder directions [deg].

        The values are used once at startup of the client to set the directions of range finders.
        During regular execution, a 19-valued vector of track distances in these directions is
        returned in ``state.State.tracks``.
        """
        return -90, -75, -60, -45, -30, -20, -15, -10, -5, 0, 5, 10, 15, 20, 30, 45, 60, 75, 90

    def get_track_limit_coordinates(self, carstate):
        trackLimitCoordinatesX = []
        trackLimitCoordinatesY = []
        offroad = True

        assert self.rangeFinderAngles[self.NULL_INDEX] == 0
        for index, measurement in enumerate(carstate.distances_from_edge):
            if measurement > -1:
                offroad = False
                trackLimitCoordinatesX.append(measurement * math.cos(self.rangeFinderAngles[index] / 180 * math.pi))
                trackLimitCoordinatesY.append(-1 * measurement * math.sin(self.rangeFinderAngles[index] / 180 * math.pi))
        return offroad, trackLimitCoordinatesX, trackLimitCoordinatesY

    def get_Target(self, trackLimitCoordinatesX, trackLimitCoordinatesY):
        leftTrackBorderX = 0
        leftTrackBorderY = 0
        rightTrackBorderX = 0
        rightTrackBorderY = 0
        for x, y in zip(trackLimitCoordinatesX, trackLimitCoordinatesY):
            if x > leftTrackBorderX and y >= 0:
                leftTrackBorderX = x
                leftTrackBorderY = y

            if x > leftTrackBorderX and y <= 0:
                rightTrackBorderX = x
                rightTrackBorderY = y
        targetX = (rightTrackBorderX + leftTrackBorderX) / 2
        targetY = (leftTrackBorderY + rightTrackBorderY) / 2
        return targetX, targetY

    def curve_Detection(self, carstate):
        rightCurve = False
        leftCurve = False
        if carstate.distances_from_edge[self.NULL_INDEX] != -1 and carstate.distances_from_edge[self.NULL_INDEX + 2] != -1 and (
            carstate.distances_from_edge[self.NULL_INDEX] < carstate.distances_from_edge[self.NULL_INDEX + 2]):
            rightCurve = True
        if carstate.distances_from_edge[self.NULL_INDEX] != -1 and carstate.distances_from_edge[self.NULL_INDEX - 2] != -1 and carstate.distances_from_edge[
            self.NULL_INDEX] < carstate.distances_from_edge[self.NULL_INDEX - 2]:
            leftCurve = True
        self.leftCurveAverage.pop(0)
        self.rightCurveAverage.pop(0)
        self.leftCurveAverage.append(leftCurve)
        self.rightCurveAverage.append(rightCurve)
        return all(item == True for item in self.leftCurveAverage), all(item == True for item in self.rightCurveAverage)

    def get_curve_corrected_target(self, carstate, leftCurve, rightCurve, targetX, targetY):
        TRACK_WIDTH = 12
        if rightCurve:
            targetX -= TRACK_WIDTH * 2
            if targetX > 50:
                targetY += TRACK_WIDTH / 4 - (carstate.distance_from_center * TRACK_WIDTH)
        if leftCurve:
            targetX -= TRACK_WIDTH * 2
            if targetX > 50:
                targetY += TRACK_WIDTH / 4 - (carstate.distance_from_center * TRACK_WIDTH)
        return targetX, targetY

    def get_average_angle(self, angle):
        self.anglesAverage.pop(0)
        self.anglesAverage.append(angle)
        averageAngle = sum(self.anglesAverage) / len(self.anglesAverage)
        return averageAngle

    def get_offroad_target(self, angle, carstate, distance, offroad):
        if (offroad):
            CORRECTION_ANGLE = -5
            CORRECTION_DISTANCE = 10
            distance = CORRECTION_DISTANCE
            if carstate.distance_from_center <= -1:  # Right track border
                if carstate.angle == 0:
                    angle = CORRECTION_ANGLE
                elif carstate.angle > 90 or carstate.angle < -90:
                    angle = 0
                    # TODO
                elif carstate.angle > 0:
                    angle = -carstate.angle
                else:
                    angle = carstate.angle
            elif carstate.distance_from_center >= 1:  # Left track border
                if carstate.angle == 0:
                    angle = -CORRECTION_ANGLE
                elif carstate.angle > 90 or carstate.angle < -90:
                    angle = 0
                    # TODO
                elif carstate.angle > 0:
                    angle = carstate.angle
                else:
                    angle = -carstate.angle
        return angle, distance

    def get_angle_distance_from_target_coordinates(self, targetX, targetY):
        distance = math.sqrt(targetX * targetX + targetY * targetY)
        if (targetX > 0):
            angle = math.atan(targetY / targetX) * 180 / math.pi
        else:
            angle = 0

        return angle, distance

    def update(self, carstate: State) -> Coordinate:
        offroad, trackLimitCoordinatesX, trackLimitCoordinatesY = self.get_track_limit_coordinates(carstate)
        targetX, targetY = self.get_Target(trackLimitCoordinatesX, trackLimitCoordinatesY)
        leftCurve, rightCurve = self.curve_Detection(carstate)
        #targetX, targetY = self.get_curve_corrected_target(carstate, leftCurve, rightCurve, targetX, targetY)
        angle, distance = self.get_angle_distance_from_target_coordinates(targetX, targetY)
        angle, distance = self.get_offroad_target(angle, carstate, distance, offroad)
        averageAngle = self.get_average_angle(angle)

        # Debug messages
        print(offroad, carstate.angle, distance, angle, averageAngle)
        #print(carstate.distances_from_edge)
        #print(trackLimitCoordinatesX)
        #print(trackLimitCoordinatesY)
        #print(leftTrackBorderX, leftTrackBorderY, rightTrackBorderX, rightTrackBorderY)
        #print(targetX, targetY)
        #print(distance, angle)
        if leftCurve or rightCurve:
            print('########################')
            print(leftCurve, rightCurve)
            print('########################')


        return Coordinate(distance, averageAngle)