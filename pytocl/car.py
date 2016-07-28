import logging
from functools import partialmethod

import math

_logger = logging.getLogger(__name__)

DEGREE_PER_RADIANS = 180 / math.pi
MPS_PER_KMH = 1000 / 3600


class State:
    """State of car and environment, sent periodically by racing server.

    Update the state's dictionary and use properties to access the various sensor values. Value
    ``None`` means the sensor value is invalid or unset.

    Attributes:
        sensor_dict: Dictionary of sensro key value pairs in string form.
        angle: Angle between car direction and track axis, [-180; 180], deg.
        current_lap_time: Time spent in current lap, [0; inf[, s.
        damage: Damage points, 0 means no damage, [0; inf[, points.
        distance_from_start: Distance of car from start line along track center, [0; inf[, m.
        distance_raced: Distance car traveled since beginning of race, [0; inf[, m.
        fuel: Current fuel level, [0;inf[, l.
        gear: Current gear. -1: reverse, 0: neutral, [1; 6]: corresponding forward gear.
        last_lap_time: Time it took to complete last lap, [0; inf[, s.
        opponents: Distances to nearest opponents in 10 deg slices in [-180; 180] deg. [0; 200], m.
        race_position: Position in race with respect to other cars, [1; N].
        rpm: Engine's revolutions per minute, [0; inf[.
        speed: Speed in X (forward), Y (left), Z (up) direction, ]-inf; inf[, m/s.
        distances_from_edge: Distances to track edge along configured driver range finders,
            [0; 200], m.
        focused_distances_from_egde: Distances to track edge, five values in five degree range along
            driver focus, [0; 200], m. Can be used only once per second and while on track,
            otherwise values invalid (-1).
        distance_from_center: Normalized distance from track center, -1: right edge, 0: center,
            1: left edge, [0; 1].
        wheel_velocities: Four wheels' velocity, [0; inf[, deg/s.
        z: Distance of car center of mass to track surface, ]-inf; inf[, m.
    """

    def __init__(self):
        self.sensor_dict = None
        self.angle = 0.0
        self.current_lap_time = 0.0
        self.damage = 0
        self.distance_from_start = 0.0
        self.distance_raced = 0.0
        self.fuel = 0.0
        self.gear = 0
        self.last_lap_time = 0.0
        self.opponents = tuple(200 for _ in range(36))
        self.race_position = 1
        self.rpm = 0.0
        self.speed = (0.0, 0.0, 0.0)
        self.distances_from_edge = tuple(200.0 for _ in range(19))
        self.focused_distances_from_egde = tuple(200.0 for _ in range(5))
        self.distance_from_center = 0.0
        self.wheel_velocities = (0.0, 0.0, 0.0, 0.0)
        self.z = 0.0

    def __str__(self):
        kvs = ('{}: {}'.format(k, v) for k, v in self.__dict__.items() if k != 'sensor_dict')
        return '\n'.join(kvs)

    def update(self, sensor_dict):
        """Updates state data from key value strings in sensor dictionary."""
        self.sensor_dict = sensor_dict
        self.angle = self.float_value('angle') * DEGREE_PER_RADIANS
        self.current_lap_time = self.float_value('curLapTime')
        self.damage = self.int_value('damage')
        self.distance_from_start = self.float_value('distFromStart')
        self.distance_raced = self.float_value('distRaced')
        self.fuel = self.float_value('fuel')
        self.gear = self.int_value('gear')
        self.last_lap_time = self.float_value('lastLapTime')
        self.opponents = self.floats_value('opponents')
        self.race_position = self.int_value('racePos')
        self.rpm = self.float_value('rpm')
        self.speed = (self.float_value('speedX') * MPS_PER_KMH,
                      self.float_value('speedY') * MPS_PER_KMH,
                      self.float_value('speedZ') * MPS_PER_KMH)
        self.distances_from_edge = self.floats_value('track')
        self.focused_distances_from_egde = self.floats_value('focus')
        self.distance_from_center = self.float_value('trackPos')
        self.wheel_velocities = tuple(v * DEGREE_PER_RADIANS for v in
                                      self.floats_value('wheelSpinVel'))
        self.z = self.float_value('z')

    def converted_value(self, key, converter):
        try:
            return converter(self.sensor_dict[key])
        except (ValueError, KeyError):
            _logger.warning('Expected sensor value {!r} not found.'.format(key))
            return None

    float_value = partialmethod(converted_value, converter=float)
    floats_value = partialmethod(converted_value, converter=lambda l: tuple(float(v) for v in l))
    int_value = partialmethod(converted_value, converter=int)


class Command:
    """Command to drive car during next control cycle."""
