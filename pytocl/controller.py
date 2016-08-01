import abc


class Controller(abc.ABC):
    """Base class for a numeric controller."""

    @abc.abstractmethod
    def control(self, deviation) -> float:
        """Compute control variable from deviation of outputs."""

    def reset(self):
        """Resets any history that my be stored in controller state."""


class ProportionalController(Controller):
    """Proportinal controller.

    Attributes:
        gain: Factor applied to deviation.
    """

    def __init__(self, gain):
        self.gain = gain

    def control(self, deviation):
        return self.gain * deviation
