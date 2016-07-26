from typing import Optional

import math


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


DEGREE_PER_RAD = 180 / math.pi


class CarState:
    """State of car and environment, sent periodically by racing server.

    Update the state's dictionary and use properties to access the various sensor values. Value
    ``None`` means the sensor value is invalid or unset.
    """

    def __init__(self):
        #: Dictionary of sensor values in string representation.
        self.sensor_dict = {}

    @property
    def angle(self) -> Optional[float]:
        """Angle between car direction and track axis, [-180; 180] degrees."""
        return self._float_value('angle', DEGREE_PER_RAD)

    def _float_value(self, key, factor=1):
        value_str = self.sensor_dict.get(key)
        return float(value_str) * factor if value_str else None
