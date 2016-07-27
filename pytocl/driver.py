import logging
import math
from functools import partialmethod
from typing import Optional

_logger = logging.getLogger(__name__)


class Driver:
    """Driving logic.

    Implement the driving intelligence in this class by processing the current car state as inputs
    creating car control commands as a response. The ``drive`` function is called periodically
    every 20ms and must return a command within 10ms wall time.
    """

    @property
    def range_finder_angles(self):
        """Iterable of 19 fixed range finder directions [deg].

        The values are used once at startup of the client to set the directions of range finders.
        During regular execution, a 19-valued vector of track distances in these directions is
        returned in ``state.State.tracks``.
        """
        return -90, -75, -60, -45, -30, -20, -15, -10, -5, 0, 5, 10, 15, 20, 30, 45, 60, 75, 90

    def on_restart(self):
        """Server requested driver restart.

        Optionally implement this event handler to reinitialize internal data structures of the
        driving logic.
        """

    def on_shutdown(self):
        """Server requested driver shutdown.

        Optionally implement this event handler to clean up or write data before the application is
        stopped.
        """


class CarState:
    """State of car and environment, sent periodically by racing server.

    Update the state's dictionary and use properties to access the various sensor values. Value
    ``None`` means the sensor value is invalid or unset.

    Attributes:
        sensor_dict: Dictionary of sensro key value pairs in string form.
        angle: Angle between car direction and track axis, [-pi; pi], rad.
        current_lap_time: Time spent in current lap, [0; inf[, sec.
        damage: Damage points, 0 means no damage, [0; inf[, points.
    """

    def __init__(self):
        self.sensor_dict = None
        self.angle = 0.0
        self.current_lap_time = 0.0
        self.damage = 0

    def update(self, sensor_dict):
        """Updates state data from key value strings in sensor dictionary."""
        self.sensor_dict = sensor_dict
        self.angle = self.float_value('angle')
        self.current_lap_time = self.float_value('curLapTime')
        self.damage = self.int_value('damage')

    def converted_value(self, key, converter):
        try:
            return converter(self.sensor_dict[key])
        except (ValueError, KeyError):
            _logger.warning('Expected sensor value {!r} not found.'.format(key))
            return None

    float_value = partialmethod(converted_value, converter=float)
    int_value = partialmethod(converted_value, converter=int)
