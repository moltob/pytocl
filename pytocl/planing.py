from pytocl.car import State, CustomData
from collections import namedtuple
import logging

_logger = logging.getLogger(__name__)

TrackSection = namedtuple('TrackSection', ['start', 'end', 'max_speed', 'target_pos'])


class PlaningController:
    def __init__(self):
        self.lap = 0
        self.last_distance_from_start = 0
        self.store_last_distance_from_start = 0
        self.track_plan = [
            TrackSection(start=0.0, end=50.0, max_speed=600, target_pos=0.5),
            TrackSection(start=50.0, end=220.0, max_speed=600, target_pos=0.3),
            TrackSection(start=220.0, end=2450.0, max_speed=600, target_pos=0.4),
            TrackSection(start=2450.0, end=2500.0, max_speed=10, target_pos=0.0)
        ]

    def control(self, carstate: State, custom_data: CustomData):
        self.detect_lap(carstate)
        _logger.info('Distance_from_start: {}'.format(carstate.distance_from_start))
        if self.lap != 0:
            for section in self.track_plan:
                if section.start < carstate.distance_from_start and section.end > carstate.distance_from_start:
                    _logger.info('Detected section: {}'.format(section))
                    return section.max_speed, section.target_pos
        return 600, 0

    def detect_lap(self, carstate: State):
        if self.store_last_distance_from_start < 10:
            self.store_last_distance_from_start += 1
        else:
            self.store_last_distance_from_start = 0

            if int(self.last_distance_from_start) > int(carstate.distance_from_start):
                self.lap += 1
            self.last_distance_from_start = carstate.distance_from_start
