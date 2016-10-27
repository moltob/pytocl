from pytocl.car import State
from .Coordinate import Coordinate
class TrajectoryPlanner:
    def __init__(self):
        pass

    @property
    def range_finder_angles(self):
        """Iterable of 19 fixed range finder directions [deg].

        The values are used once at startup of the client to set the directions of range finders.
        During regular execution, a 19-valued vector of track distances in these directions is
        returned in ``state.State.tracks``.
        """
        return -90, -75, -60, -45, -30, -20, -15, -10, -5, 0, 5, 10, 15, 20, 30, 45, 60, 75, 90

    def update(self, carstate: State) -> Coordinate:
        target = Coordinate(0, 0)

        angle = carstate.angle

        for measurement in carstate.distances_from_edge:
            print(measurement)

        return target