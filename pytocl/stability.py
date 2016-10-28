from pytocl.car import Command, State, MPS_PER_KMH
import logging

_logger = logging.getLogger(__name__)


class StabilityController:
    def __init__(self):
        self.gb_controller = GearboxController(1)
        self.steering_controller = SteeringController()
        self.velocity_controller = VelocityController()
        self.lastgear = 0

    def control(self, target_speed, target_pos, car_state: State):
        command = Command()

        command.gear = self.gb_controller.control(car_state.rpm, car_state.gear)

        command.steering = self.steering_controller.control(target_pos, car_state.angle, car_state.distance_from_center)
        if command.gear != self.lastgear:
            geardown = True
        else:
            geardown = False
        (command.accelerator, command.brake) = self.velocity_controller.control(target_speed,
                                                                                car_state.speed_x, geardown)
        self.lastgear = command.gear
        return command


class GearboxController:
    def __init__(self, gear):
        self.gear_control = gear

    def control(self, rpm, gear):
        # gear shifting:
        self.gear_control = gear or 1
        if rpm > 9000 and gear < 6:
            #_logger.info('switching up')
            self.gear_control = gear + 1
        elif rpm < 4000 and gear > 2:
            #_logger.info('switching down')
            self.gear_control = gear - 1
        elif rpm < 3100 and gear > 1:
            self.gear_control = gear - 1

        #_logger.info('GearboxController: rpm, gear, gear_control: {}, {}, {}'.format(rpm, gear, self.gear_control))
        return self.gear_control


class SteeringController:
    def __init__(self):
        pass

    def control(self, target_pos, angle, distance_from_center):
        distance_from_target_pos = target_pos - distance_from_center
        steering = (angle / 21) + distance_from_target_pos * 0.5
        #_logger.info('SteeringController: target_pos, angle, distance_from_center, steering: {}, {}, {}, {}'.
        #             format(target_pos, angle, distance_from_center, steering))

        return steering


class VelocityController:
    def __init__(self):
        self.accelerator = 0.0
        self.brake = 0.0

    def control(self, target_speed_x, current_speed_x, geardown):
        # basic acceleration to target speed:
        speed_diff = target_speed_x * MPS_PER_KMH - current_speed_x
        if speed_diff > 0:
            if self.accelerator < 0.7 and current_speed_x < 25:
                self.accelerator += 0.1
                self.accelerator = max(0.3, self.accelerator)
            elif geardown:
                self.accelerator = 0.5
            else:
                self.accelerator = 1.0

            self.brake = 0.0

        else:
            self.accelerator = 0.0
            self.brake = -speed_diff * 0.1

        self.accelerator = min(1, self.accelerator)
        self.accelerator = max(-1, self.accelerator)
        #_logger.info('VelocityController: speed_x, accelerator: {}, {}'.
        #             format(target_speed_x, self.accelerator))
        return self.accelerator, self.brake
