import logging

from pytocl.car import State, Command
from pytocl.controller import CompositeController, ProportionalController, IntegrationController, \
    DerivativeController

_logger = logging.getLogger(__name__)


class Driver:
    """Driving logic.

    Implement the driving intelligence in this class by processing the current car state as inputs
    creating car control commands as a response. The ``drive`` function is called periodically
    every 20ms and must return a command within 10ms wall time.
    """

    def __init__(self):
        self.steering_pid = CompositeController(
            ProportionalController(-1),
            IntegrationController(-0.2, 1.5),
            DerivativeController(-4)
        )

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
        self.steering_pid.reset()

    def on_shutdown(self):
        """Server requested driver shutdown.

        Optionally implement this event handler to clean up or write data before the application is
        stopped.
        """

    def drive(self, carstate: State) -> Command:
        """Produces driving command in response to newly received car state.

        This is a dummy driving routine, very dumb and not really considering a lot of inputs. But
        it will get the car (if not disturbed by other drivers) successfully driven along the race
        track.
        """
        command = Command()
        command.steering = self.steering_pid.control(carstate.distance_from_center + 0.55,
                                                     carstate.current_lap_time)
        print('Steering angle: {}'.format(self.steering_pid))

        target_speed = 10

        # reach target velocity:
        if carstate.rpm > 8000:
            command.gear = carstate.gear + 1
        elif carstate.rpm < 2500 and carstate.gear > 1:
            command.gear = carstate.gear - 1
        else:
            command.gear = carstate.gear or 1

        if carstate.speed_x < target_speed:
            command.accelerator = 1

        return command
