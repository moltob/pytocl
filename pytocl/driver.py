import logging

from pytocl.car import State, Command

_logger = logging.getLogger(__name__)


class Driver:
    """Driving logic.

    Implement the driving intelligence in this class by processing the current car state as inputs
    creating car control commands as a response. The ``drive`` function is called periodically
    every 20ms and must return a command within 10ms wall time.
    """

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

        # align the car direction with the direction of the track:
        command.steering = 0.3 * carstate.angle - (0.7 * carstate.distance_from_center)

        target_speed = 20

        # reach target velocity:
        if carstate.rpm > 8000:
            command.gear = carstate.gear + 1
        elif carstate.rpm < 2500 and carstate.gear > 1:
            command.gear = carstate.gear - 1
        else:
            command.gear = carstate.gear or 1

        if carstate.speed[0] < target_speed:
            command.accelerator = 1

        return command
