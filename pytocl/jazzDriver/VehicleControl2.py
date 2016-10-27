from pytocl.car import State, Command, MPS_PER_KMH
from .Coordinate import Coordinate
import logging

_logger = logging.getLogger(__name__)

class VehicleControl2:
    def __init__(self):
        self.accelerator = 0.0
        self.steering = 0
        self.gear = 0

    def saturate(val, mini, maxi):
        val_sat = val
        val_sat = min(maxi, val_sat)
        val_sat = max(mini, val_sat)
        return val_sat

    def calc_lenkwinkel(self, target: Coordinate, carstate: State):
        self.steering = target.angle
        self.steering = VehicleControl.saturate(self.steering, -180, 180)

    def mock_lenkwinkel(self, carstate):
        return (carstate.angle - carstate.distance_from_center * 0.5)

    def calc_accelerator(self, target: Coordinate, carstate: State):
        # basic acceleration to target speed:
        if carstate.speed_x < 30 * MPS_PER_KMH:
            self.accelerator += 0.01
        else:
            accelerator = 0
        self.accelerator = VehicleControl.saturate(self.accelerator, 0, 0.5)

    def calc_gear(self, target: Coordinate, carstate: State):
        self.gear = carstate.gear or 1
        if carstate.rpm > 5000 and carstate.gear < 6:
            _logger.info('switching up')
            self.gear = carstate.gear + 1
        elif carstate.rpm < 2000 and carstate.gear > 1:
            _logger.info('switching down')
            self.gear = carstate.gear - 1

    def driveTo(self, target: Coordinate, carstate: State) -> Command:

        _logger.info('carstate.rpm, carstate.gear: {}, {}'.format(carstate.rpm, carstate.gear))
        command = Command()

        target.angle = self.mock_lenkwinkel(carstate) # weg!!!!
        self.calc_lenkwinkel(target, carstate)
        self.calc_accelerator(target, carstate)
        self.calc_gear(target, carstate)

        command.steering = self.steering
        _logger.info('steering: {}'.format(command.steering))
        command.accelerator = self.accelerator
        _logger.info('accelerator: {}'.format(command.accelerator))
        command.gear = self.gear
        _logger.info('gear: {}'.format(command.gear))

        return command

