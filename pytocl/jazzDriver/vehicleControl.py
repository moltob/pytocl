from pytocl.car import State, Command, MPS_PER_KMH
from .Coordinate import Coordinate
import logging

_logger = logging.getLogger(__name__)

TRACK_WIDTH = 12
DISTANCE_EMERGENCY_BRAKE = 13
SAFE_CORNERING_SPEED = 50

class VehicleControl:
    def __init__(self):
        self.gear = 0
        self.AbsCounter = 0
        self.VehicleOverGroundStd = 0
        self.LandungsBremsCounter = 0       #brake for so many cycles. gets set when we land after liftoff

    def saturate(val, mini, maxi):
        val_sat = val
        val_sat = min(maxi, val_sat)
        val_sat = max(mini, val_sat)
        return val_sat

    def calc_lenkradwinkel(self, wanted_radwinkel):
        normlized_lenkradwinkel = wanted_radwinkel/21 #weil range von -1..1
        return normlized_lenkradwinkel

    def calc_radwinkel(self, wanted_zielwinkel):
        return VehicleControl.saturate(wanted_zielwinkel, -21, 21)  #weil nur in diesem bereich lenkbar


    def calc_max_accel_angle(self, a_radwinkel, distance):
        if(distance==0):
            accel = 0
        else:
            radwinkel = abs(a_radwinkel)
            if(radwinkel < 1):
                accel = 1
            elif (radwinkel < 2):
                accel = 1
            elif(radwinkel < 3):
                accel = .9
            elif(radwinkel < 4):
                accel = .8
            elif(radwinkel < 5):
                accel = .7
            else:
                accel = .6
        VehicleControl.saturate(accel, 0, 1)
        return accel

    def calc_max_decel_angle(self, a_radwinkel, speed):
        radwinkel = abs(a_radwinkel)
        if(radwinkel < 2):
            decel = 1
        elif (radwinkel < 4):
            decel = 1
        elif(radwinkel < 6):
            decel = 1
        elif(radwinkel < 8):
            decel = 1
        elif(radwinkel < 10):
            decel = 1
        else:
            decel = 1
        VehicleControl.saturate(decel, 0, 1)
        return decel

    def calc_gear(self, target: Coordinate, carstate: State):
        self.gear = carstate.gear or 1
        if carstate.rpm > 9000 and carstate.gear < 6:
#            _logger.info('switching up')
            self.gear = carstate.gear + 1
        elif carstate.rpm < 4000 and carstate.gear > 1:
#            _logger.info('switching down')
            self.gear = carstate.gear - 1

    def isOffroad(self, carstate: State):
        isOffRoad = not carstate.distances_from_egde_valid
        if(isOffRoad):
            _logger.info('####################################################### offroad ##########################################')
        return isOffRoad

    def getEmergencyBrakeDistance(self, carstate: State):
        return carstate.speed_x / 1.3   #1.7 auch ok aber wackelig


    def get_max_grippy_speed(self, a_radwinkel, carstate:State, target: Coordinate):
        radwinkel = abs(a_radwinkel)
        if( self.isOffroad(carstate)):
            speed_mph = 10
        else:
             if (target.distance < self.getEmergencyBrakeDistance(carstate)):
                 speed_mph = SAFE_CORNERING_SPEED
             else:
                 if(radwinkel < 1):
                    speed_mph = 140
                 elif (radwinkel < 2):
                    speed_mph = 130
                 elif(radwinkel < 3):
                    speed_mph = 120
                 elif(radwinkel < 4):
                    speed_mph = 70
                 elif(radwinkel < 5):
                    speed_mph = 60
                 else:
                    speed_mph = SAFE_CORNERING_SPEED

        speed = speed_mph/3.6  #mps

        VehicleControl.saturate(speed, 0, 300)
        return speed


    def getWantedZielwinkelInCurrentInvocation(self, zielwinkel, carstate: State, target: Coordinate):
        if(carstate.speed_x == 0 or target.distance == 0):
            time_till_targetpoint_s = 5
        else:
            time_till_targetpoint_s = target.distance / carstate.speed_x
        expected_number_of_subsequent_invokations_till_targetpoint = time_till_targetpoint_s * 5 #50 invocations per second
        wanted_zielwinkel_in_current_invokation = zielwinkel / expected_number_of_subsequent_invokations_till_targetpoint;

        wanted_zielwinkel_in_current_invokation = zielwinkel    #der Scheiß davor funktioniert nicht -> überschreiben

        return wanted_zielwinkel_in_current_invokation




    def driveTo(self, target: Coordinate, carstate: State) -> Command:

        if(carstate.speed_x <= 1 and self.VehicleOverGroundStd == 0):
            self.VehicleOverGroundStd = carstate.z

        command = Command()

        self.calc_gear(target, carstate)

        #when we're offroad then we dot get distances. set it hard to 2 meters. max_grippy_speed will also be reduced then
        if(self.isOffroad(carstate)):
            target.distance = 2

        #Lenkwinkel und Co
        wanted_zielwinkel = target.angle
        wanted_zielwinkel_in_current_invokation = self.getWantedZielwinkelInCurrentInvocation(wanted_zielwinkel, carstate, target)
        radwinkel = self.calc_radwinkel(wanted_zielwinkel_in_current_invokation)

        #ignore small radwinkel at low speed
        if(carstate.speed_x < 20 and abs(radwinkel) < 2 and target.distance > 5):
            radwinkel = 0

        if( carstate.z > self.VehicleOverGroundStd + 0.04 and carstate.speed_x > 10):
            _logger.info('abgehoben z={}, std={}'.format(carstate.z, self.VehicleOverGroundStd))
            self.LandungsBremsCounter = 5

        if(self.LandungsBremsCounter > 0):
            self.LandungsBremsCounter-=1
            radwinkel = 0                       #overwrite radwinkel for landing
            required_accel_angle = 0
            required_brake_angle = 1
            _logger.info(
                '####################### radwinkel={}, reqBrackeAngle={}, distance={}, speed={}'.format(
                    radwinkel, required_brake_angle, target.distance, carstate.speed_x))
        else:
            required_accel_angle, required_brake_angle = self.calc_accelerations_normal_mode(carstate, radwinkel, target)


        lenkradwinkel = self.calc_lenkradwinkel(radwinkel)

        #in offroad better not brake
#        if(self.isOffroad(carstate)):
#            required_brake_angle = 0

        #command object befüllen
        command.brake = required_brake_angle
        command.accelerator = required_accel_angle
     #   _logger.info('accelerator: {}'.format(command.accelerator))
     #   _logger.info('brake: {}'.format(command.brake))

        command.steering = lenkradwinkel
     #   _logger.info('steering: {}'.format(command.steering))
        command.gear = self.gear
     #   _logger.info('gear: {}'.format(command.gear))

        return command

    def calc_accelerations_normal_mode(self, carstate, radwinkel, target):
        # wie schnell können wir beschleunigen ohne abzufliegen
        max_accel_angle = self.calc_max_accel_angle(radwinkel, target.distance)
        max_grippy_speed = self.get_max_grippy_speed(radwinkel, carstate, target)
        # calc acceleration and brake force
        required_accel_angle = 0;
        required_brake_angle = 0;
        # sind wir unterhalt max_grip_speed?
        if (carstate.speed_x > max_grippy_speed):  # todo: alle speed-komponenten berücksichtigen?
            # nein, überhalb -> schauen ob wir bremsen müssen. wir können solange weiterbeschleunigen, dass wir durch eine vollbremsung auf die gripspeed runterkommen
            # es gbt 2 fälle:
            # 1 Erreichen des Targetpoints
            # 2 Fahren in der Kurve
#            radwinkel = 0   #todo: weg?
            required_brake_angle = self.calc_max_decel_angle(radwinkel, carstate.speed_x)
            required_accel_angle = 0
            _logger.info(
                '####################### max_grippy_speed={}, radwinkel={}, reqBrackeAngle={}, distance={}, speed={}'.format(
                    max_grippy_speed, radwinkel, required_brake_angle, target.distance, carstate.speed_x))
        else:
            # ja, unterhalb max_grip_speed -> so schnell beschleunigen wie mgl
            required_accel_angle = max_accel_angle
            required_brake_angle = 0
            _logger.info('max_grippy_speed={}, radwinkel={}, distance={}, speed={}'.format(max_grippy_speed, radwinkel,
                                                                                 target.distance, carstate.speed_x))
        return required_accel_angle, required_brake_angle

