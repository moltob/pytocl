import abc
import functools


class Controller(abc.ABC):
    """Base class for a numeric controller."""

    @abc.abstractmethod
    def control(self, deviation, timestamp) -> float:
        """Compute control variable from deviation of outputs."""

    def reset(self):
        """Resets any history that my be stored in controller state."""


class ProportionalController(Controller):
    """P controller.

    Attributes:
        gain: Factor applied to deviation.
    """

    def __init__(self, gain):
        self.gain = gain

    def control(self, deviation, timestamp):
        return self.gain * deviation


class DerivativeController(Controller):
    """D controller.

    Attributes:
        gain: Factor applied to differentiation of error.
    """

    def __init__(self, gain):
        self.gain = gain
        self.last_deviation = 0
        self.last_timestamp = 0

    def control(self, deviation, timestamp):
        value = self.gain * (deviation - self.last_deviation) / (timestamp - self.last_timestamp)
        self.last_deviation = deviation
        self.last_timestamp = timestamp
        return value


class CompositeController(Controller):
    def __init__(self, *controllers):
        self.controllers = controllers

    def control(self, deviation, timestamp):
        return sum(c.control(deviation, timestamp) for c in self.controllers)


def pd_controller(pgain, dgain):
    return CompositeController(ProportionalController(pgain), DerivativeController(dgain))
