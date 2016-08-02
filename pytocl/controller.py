import abc
import functools

import math


class Controller(abc.ABC):
    """Base class for a numeric controller."""

    last_value = 0.0

    @abc.abstractproperty
    def shortname(self):
        """Short name of controller type to show in logs."""

    @abc.abstractmethod
    def control(self, deviation, timestamp) -> float:
        """Compute control variable from deviation of outputs."""

    def reset(self):
        """Resets any history that my be stored in controller state."""

    def __str__(self):
        return '{}: {:-8.3f}'.format(self.shortname, self.last_value)


class ProportionalController(Controller):
    """P controller.

    Attributes:
        gain: Factor applied to deviation.
    """

    def __init__(self, gain):
        self.gain = gain

    @property
    def shortname(self):
        return 'P'

    def control(self, deviation, timestamp):
        value = self.gain * deviation
        self.last_value = value
        return value


class DerivativeController(Controller):
    """D controller.

    Attributes:
        gain: Factor applied to derivative of error.
    """

    def __init__(self, gain):
        self.gain = gain
        self.last_deviation = 0
        self.last_timestamp = 0

    @property
    def shortname(self):
        return 'D'

    def control(self, deviation, timestamp):
        value = self.gain * (deviation - self.last_deviation) / (timestamp - self.last_timestamp)
        self.last_value = value
        self.last_deviation = deviation
        self.last_timestamp = timestamp
        return value

    def reset(self):
        self.last_deviation = 0
        self.last_timestamp = 0


class IntegrationController(Controller):
    """I controller.

    Attributes:
        gain: Factor applied to derivative of error.
        integral_limit: Optional integration limit of absolute value.
    """

    def __init__(self, gain, integral_limit=None):
        self.gain = gain
        self.integral_limit = integral_limit
        self.integral = 0
        self.last_timestamp = 0

    @property
    def shortname(self):
        return 'I'

    def control(self, deviation, timestamp):
        self.integral += deviation * (timestamp - self.last_timestamp)
        if self.integral_limit and abs(self.integral) > self.integral_limit:
            self.integral = math.copysign(self.integral_limit, self.integral)
        self.last_timestamp = timestamp
        value = self.gain * self.integral
        self.last_value = value
        return value

    def reset(self):
        self.integral = 0
        self.last_timestamp = 0


class CompositeController(Controller):
    def __init__(self, *controllers):
        self.controllers = controllers

    @property
    def shortname(self):
        return 'Comp'

    def control(self, deviation, timestamp):
        return sum(c.control(deviation, timestamp) for c in self.controllers)

    def __str__(self):
        return ', '.join(str(c) for c in self.controllers)
