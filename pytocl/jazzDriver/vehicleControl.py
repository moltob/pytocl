from pytocl.car import State, Command, MPS_PER_KMH
from .Coordinate import Coordinate
import logging

_logger = logging.getLogger(__name__)

class VehicleControl:
    def __init__(self):
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

    def calc_max_accel(self, lenkwinkel):
        accel = .5
        #todo: schön machen
        VehicleControl.saturate(accel, 0, 1)
        return accel

    def calc_max_decel(self, lenkwinkel, speed):
        decel = .3
        #todo: schön machen
        VehicleControl.saturate(decel, 0, 1)
        return decel

    def calc_gear(self, target: Coordinate, carstate: State):
        self.gear = carstate.gear or 1
        if carstate.rpm > 9000 and carstate.gear < 6:
            _logger.info('switching up')
            self.gear = carstate.gear + 1
        elif carstate.rpm < 2000 and carstate.gear > 1:
            _logger.info('switching down')
            self.gear = carstate.gear - 1


    def get_max_grippy_speed(self, lenkwinkel):
        speed = 60/3.6
        #todo: schön machen
        VehicleControl.saturate(speed, 0, 300)
        return speed

    def getBrakeAngleFromDecel(self, decel):
        return 0.5

    def driveTo(self, target: Coordinate, carstate: State) -> Command:

        _logger.info('carstate.rpm, carstate.gear: {}, {}'.format(carstate.rpm, carstate.gear))
        command = Command()

        target.angle = self.mock_lenkwinkel(carstate) # weg!!!!
        self.calc_lenkwinkel(target, carstate)
        #wie schnell können wir beschleunigen ohne abzufliegen
        max_accel = self.calc_max_accel(self.steering)
        self.calc_gear(target, carstate)

        lenkwinkel_at_targetpoint = 10      #damit wir nicht mit geraden rädern ankommen und denken wir würden nicht rutschen
        max_grippy_speed_at_targetpoint = self.get_max_grippy_speed(lenkwinkel_at_targetpoint)

        if( carstate.speed_x > max_grippy_speed_at_targetpoint  ): #todo: alle speed-komponenten berücksichtigen?
            time_till_targetpoint = target.distance / carstate.speed_x
            if(time_till_targetpoint > 0):
                required_decel = (carstate.speed_x - max_grippy_speed_at_targetpoint) / time_till_targetpoint
                #todo: müssen erst im letzten moment bremsen
                required_brake_angle = self.getBrakeAngleFromDecel(required_decel)
            else:
                required_brake_angle = 0
            command.brake = required_brake_angle
            command.accelerator = 0
        else:
            command.accelerator = max_accel
            command.brake = 0

        _logger.info('accelerator: {}'.format(command.accelerator))
        _logger.info('brake: {}'.format(command.brake))

        command.steering = self.steering
        _logger.info('steering: {}'.format(command.steering))
        command.gear = self.gear
        _logger.info('gear: {}'.format(command.gear))

        return command

