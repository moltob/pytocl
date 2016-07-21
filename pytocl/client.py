import argparse
import enum
import logging

from .driver import Driver

_logger = logging.getLogger(__name__)


class Client:
    """Client for TORCS racing car simulation with SCRC network server.

    Attributes:
        hostname (str): Server hostname.
        port (int): Port number to connect, from 3001 to 3010 for ten clients.
        bot_id (str): Name of driving bot.
        driver (Driver): Driving logic implementation.
        state (State): Runtime state of the client.
    """

    def __init__(self, hostname='localhost', port=3001, *, bot_id='SCR', driver=None):
        self.hostname = hostname
        self.port = port
        self.bot_id = bot_id
        self.driver = driver or Driver()
        self.state = State.STOPPED

    def start(self):
        """Enters cyclic execution of the client network interface."""

        if self.state is State.STOPPED:
            _logger.debug('Starting cyclic execution.')

            self.state = State.STARTING

            try:
                _logger.info('Connecting to {s.hostname}:{s.port}.'.format(s=self))

                # todo: connect to server
                self.state = State.RUNNING

                _logger.debug('Connection successful.')

            except Exception as ex:  # todo: reduce catch clause scope
                _logger.error('Cannot connect to server: {}'.format(ex))
                self.state = State.STOPPED

    def stop(self):
        """Exits cyclic client execution (asynchronously)."""
        if self.state is State.RUNNING:
            _logger.info('Disconnecting from racing server.')
            self.state == State.STOPPING


class State(enum.Enum):
    """The runtime state of the racing client."""

    # not connected to a racing server
    STOPPED = 1,
    # entering cyclic execution
    STARTING = 2,
    # connected to racing server and evaluating driver logic
    RUNNING = 3,
    # exiting cyclic execution loop
    STOPPING = 4,
