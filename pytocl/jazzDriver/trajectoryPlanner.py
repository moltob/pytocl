from pytocl.car import State
from .Coordinate import Coordinate
class TrajectoryPlanner():
    def __init__(self):
        pass

    def update(self, carstate: State) -> Coordinate:
        target = Coordinate()
        return target