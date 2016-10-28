from pytocl.car import State, Command, MPS_PER_KMH, CustomData
import logging
from enum import Enum

_logger = logging.getLogger(__name__)


class EmergencyController:
    def __init__(self):
        self.stuck_time = 0
        self.emergency_active = False
        self.emergency_time = 0
        self.steering_angle = 0


    def control(self, carstate: State, command: Command, custom_data: CustomData):
        if False == self.emergency_active:
            slow_speed = False
            off_track = False

            if carstate.speed_x * MPS_PER_KMH < 1.0:
                slow_speed = True

            if carstate.distances_from_edge[9] < 0:
                off_track = True

            if slow_speed and off_track:
                self.stuck_time += 1
            else:
                self.stuck_time = 0

            if self.stuck_time > 500:
                self.emergency_active = True
                self.emergency_time = 0
                self.stuck_time = 0
                self.steering_angle = command.steering

        if True == self.emergency_active:
            self.emergency_time += 1
            command.gear = -1
            command.accelerator = 0.2
            command.brake = 0.0
            command.steering = self.steering_angle

            if self.emergency_time > 500:
                self.emergency_active = False
                self.emergency_time = 0
                self.stuck_time = 0
