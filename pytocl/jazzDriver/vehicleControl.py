from pytocl.car import State, Command, MPS_PER_KMH
from .Coordinate import Coordinate
import logging

_logger = logging.getLogger(__name__)

TRACK_WIDTH = 12
DISTANCE_EMERGENCY_BRAKE = 12
SAFE_CORNERING_SPEED = 50

class VehicleControl:
    def __init__(self):
        self.gear = 0
        self.AbsCounter = 0

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
                accel = .9
            elif(radwinkel < 3):
                accel = .8
            elif(radwinkel < 4):
                accel = .7
            elif(radwinkel < 5):
                accel = .6
            else:
                accel = .5
        VehicleControl.saturate(accel, 0, 1)
        return accel

    def calc_max_decel_angle(self, a_radwinkel, speed):
        radwinkel = abs(a_radwinkel)
        if(radwinkel < 2):
            decel = 1
        elif (radwinkel < 4):
            decel = 1
        elif(radwinkel < 6):
            decel = .9
        elif(radwinkel < 8):
            decel = .9
        elif(radwinkel < 10):
            decel = .8
        else:
            decel = .7
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
        #isOffRoad = (carstate.distance_from_center > ((TRACK_WIDTH/2)-2) )
        isOffRoad = not carstate.distances_from_egde_valid
        if(isOffRoad):
            _logger.info('####################################################### offroad ##########################################')
        return isOffRoad

    def getEmergencyBrakeDistance(self, carstate: State):
        return carstate.speed_x / 1.5


    def get_max_grippy_speed(self, a_radwinkel, carstate:State, target: Coordinate):
        radwinkel = abs(a_radwinkel)
        if( self.isOffroad(carstate)):
            speed_mph = 5
        else:
             if (target.distance < self.getEmergencyBrakeDistance(carstate)):
                 speed_mph = SAFE_CORNERING_SPEED
             else:
                 if(radwinkel < 1):
                    speed_mph = 300
                 elif (radwinkel < 2):
                    speed_mph = 180
                 elif(radwinkel < 3):
                    speed_mph = 100
                 elif(radwinkel < 4):
                    speed_mph = 60
                 elif(radwinkel < 5):
                    speed_mph = 50
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

        command = Command()

        wanted_zielwinkel = target.angle
        wanted_zielwinkel_in_current_invokation = self.getWantedZielwinkelInCurrentInvocation(wanted_zielwinkel, carstate, target)
        radwinkel = self.calc_radwinkel(wanted_zielwinkel_in_current_invokation)
        lenkradwinkel = self.calc_lenkradwinkel(radwinkel)

        #when we're offroad then we dot get distances. set it hard to 2 meters. max_grippy_speed will also be reduced then
        if(self.isOffroad(carstate)):
            target.distance = 2

        #wie schnell können wir beschleunigen ohne abzufliegen
        max_accel_angle = self.calc_max_accel_angle(radwinkel, target.distance)
        self.calc_gear(target, carstate)

        max_grippy_speed = self.get_max_grippy_speed(radwinkel, carstate, target)

        #calc acceleration and brake force
        required_accel_angle = 0;
        required_brake_angle = 0;


        #sind wir unterhalt max_grip_speed?
        if( carstate.speed_x > max_grippy_speed ): #todo: alle speed-komponenten berücksichtigen?
            #nein, überhalb -> schauen ob wir bremsen müssen. wir können solange weiterbeschleunigen, dass wir durch eine vollbremsung auf die gripspeed runterkommen
            #es gbt 2 fälle:
            #1 Erreichen des Targetpoints
            #2 Fahren in der Kurve
            required_brake_angle = self.calc_max_decel_angle(radwinkel, carstate.speed_x)
            required_accel_angle = 0
            _logger.info('####################### max_grippy_speed={}, radwinkel={}, reqBrackeAngle={}, distance={}, speed={}'.format(max_grippy_speed, radwinkel, required_brake_angle, target.distance, carstate.speed_x ))
        else:
            #ja, unterhalb max_grip_speed -> so schnell beschleunigen wie mgl
            required_accel_angle = max_accel_angle
            required_brake_angle = 0
            _logger.info('max_grippy_speed={}, radwinkel={}, distance={}'.format(max_grippy_speed, radwinkel,
                                                                          target.distance))

#        if(self.AbsCounter < 10 and self.AbsCounter >= 0):
#            required_brake_angle = 0
#        elif(self.AbsCounter == 10):
#            self.AbsCounter = -10

#        self.AbsCounter += 1


        command.brake = required_brake_angle
        command.accelerator = required_accel_angle
     #   _logger.info('accelerator: {}'.format(command.accelerator))
     #   _logger.info('brake: {}'.format(command.brake))

        command.steering = lenkradwinkel
     #   _logger.info('steering: {}'.format(command.steering))
        command.gear = self.gear
     #   _logger.info('gear: {}'.format(command.gear))

        return command

