class Driver:
    """Driving logic.

    Implement the driving intelligence in this class by processing the current car state as inputs
    creating car control commands as a response. The ``drive`` function is called periodically
    every 20ms and must return a command within 10ms wall time.
    """

    def on_connect(self):
        """This driver is now managed by a client to interact with the racing server."""

    def on_disconnect(self):
        """This driver is no longer managed by a client."""
