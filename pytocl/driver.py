import datetime
import logging

import math
import os
import pickle

from pytocl.car import State, Command, MPS_PER_KMH
from pytocl.controller import CompositeController, ProportionalController, IntegrationController, \
    DerivativeController

_logger = logging.getLogger(__name__)


class Driver:
    """Driving logic.

    Implement the driving intelligence in this class by processing the current car state as inputs
    creating car control commands as a response. The ``drive`` function is called periodically
    every 20ms and must return a command within 10ms wall time.
    """

    def __init__(self, logstate=True):
        self.steering_ctrl = CompositeController(
            ProportionalController(0.4),
            IntegrationController(0.2, integral_limit=1.5),
            DerivativeController(2)
        )
        self.acceleration_ctrl = CompositeController(
            ProportionalController(3.7),
        )

        if logstate:
            dirname = 'drivelogs'
            timestr = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
            fname = 'drivelog-{}.pickle'.format(timestr)
            fpath = os.path.abspath(os.path.join(dirname, fname))
            _logger.info('Logging driver behavior to {}.'.format(fpath))

            os.makedirs(dirname, exist_ok=True)
            self.statelog_file = open(fpath, 'wb')
            self.pickler = pickle.Pickler(self.statelog_file)
        else:
            self.statelog_file = None
            self.pickler = None

        self.numlogged = 0

    @property
    def range_finder_angles(self):
        """Iterable of 19 fixed range finder directions [deg].

        The values are used once at startup of the client to set the directions of range finders.
        During regular execution, a 19-valued vector of track distances in these directions is
        returned in ``state.State.tracks``.
        """
        return -90, -75, -60, -45, -30, -20, -15, -10, -5, 0, 5, 10, 15, 20, 30, 45, 60, 75, 90

    def on_shutdown(self):
        """Server requested driver shutdown.

        Optionally implement this event handler to clean up or write data before the application is
        stopped.
        """
        if self.statelog_file:
            self.statelog_file.close()
            _logger.info('Saved {} log entries.'.format(self.numlogged))
            self.statelog_file = None
            self.pickler = None
            self.numlogged = 0

    def drive(self, carstate: State) -> Command:
        """Produces driving command in response to newly received car state.

        This is a dummy driving routine, very dumb and not really considering a lot of inputs. But
        it will get the car (if not disturbed by other drivers) successfully driven along the race
        track.
        """
        if self.pickler:
            self.pickler.dump(carstate)
            self.numlogged += 1

        command = Command()
        self.steer(carstate, 0.0, command)

        ACC_LATERAL_MAX = 6400 * 5
        v_x = min(150, math.sqrt(ACC_LATERAL_MAX / abs(command.steering)))
        print('target speed: ', v_x)

        self.accelerate(carstate, v_x, command)
        return command

    def accelerate(self, carstate, target_speed, command):
        # compensate engine deceleration, but invisible to controller to prevent braking:
        speed_error = 1.0025 * target_speed * MPS_PER_KMH - carstate.speed_x
        acceleration = self.acceleration_ctrl.control(speed_error, carstate.current_lap_time)

        # stabilize use of gas and brake:
        acceleration = math.pow(acceleration, 3)

        if acceleration > 0:
            if abs(carstate.distance_from_center) >= 1:
                # off track, reduced grip:
                acceleration = min(0.4, acceleration)

            command.accelerator = min(acceleration, 1)

            if carstate.rpm > 8000:
                command.gear = carstate.gear + 1

        else:
            command.brake = min(-acceleration, 1)

        if carstate.rpm < 2500:
            command.gear = carstate.gear - 1

        if not command.gear:
            command.gear = carstate.gear or 1

    def steer(self, carstate, target_track_pos, command):
        steering_error = target_track_pos - carstate.distance_from_center
        command.steering = self.steering_ctrl.control(steering_error, carstate.current_lap_time)
