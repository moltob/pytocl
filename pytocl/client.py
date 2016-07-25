import enum
import logging
import socket

from .driver import Driver

_logger = logging.getLogger(__name__)


class Client:
    """Client for TORCS racing car simulation with SCRC network server.

    Attributes:
        hostaddr (tuple): Tuple of hostname and port.
        port (int): Port number to connect, from 3001 to 3010 for ten clients.
        bot_id (str): Name of driving bot.
        driver (Driver): Driving logic implementation.
        serializer (Serializer): Implementation of network data encoding.
        state (State): Runtime state of the client.
        socket (socket): UDP socket to server.
    """

    def __init__(self, hostname='localhost', port=3001, bot_id=None, *,
                 driver=None, serializer=None, create_connection=None):
        self.hostaddr = (hostname, port)
        self.bot_id = bot_id or 'Dummy'
        self.driver = driver or Driver()
        self.serializer = serializer or Serializer()
        self.state = State.STOPPED
        self.socket = None

        _logger.debug('Initializing {}.'.format(self))

    def __repr__(self):
        return '{s.__class__.__name__}({s.hostaddr!r}, {s.bot_id!r}) -- ' \
               '{s.state.name}'.format(s=self)

    def start(self):
        """Enters cyclic execution of the client network interface."""

        if self.state is State.STOPPED:
            _logger.debug('Starting cyclic execution.')

            self.state = State.STARTING

            try:
                _logger.info('Registering driver {} with server {}.'.format(self.bot_id,
                                                                            self.hostaddr))
                self._configure_udp_socket()
                self._register_driver()
                self.state = State.RUNNING
                _logger.info('Connection successful.')

            except socket.error as ex:
                _logger.error('Cannot connect to server: {}'.format(ex))
                self.state = State.STOPPED

        while self.state is State.RUNNING:
            pass

        _logger.info('Client stopped.')
        self.state = State.STOPPED

    def stop(self):
        """Exits cyclic client execution (asynchronously)."""
        if self.state is State.RUNNING:
            _logger.info('Disconnecting from racing server.')
            self.state == State.STOPPING

    def _configure_udp_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(1.0)

    def _register_driver(self):
        """Sends driver's initialization data to server and waits for acceptance response."""

        angles = self.driver.range_finder_angles
        assert len(angles) == 19, \
            'Inconsistent length {} of range of finder iterable.'.format(len(angles))

        data = {'init': angles}
        buffer = self.serializer.encode(data, prefix='SCR-{}'.format(self.bot_id))

        _logger.info('Registering client.')

        connected = False
        while not connected and self.state is not State.STOPPING:
            try:
                _logger.debug('Sending init buffer {!r}.'.format(buffer))
                self.socket.sendto(buffer, self.hostaddr)

                buffer, _ = self.socket.recvfrom(1000)
                _logger.debug('Received buffer {!r}.'.format(buffer))
                if b'***identified***' in buffer:
                    _logger.debug('Server accepted connection.')
                    connected = True

            except socket.error as ex:
                _logger.debug('No connection to server yet ({}).'.format(ex))


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


class Serializer:
    """Serializer for racing data protocol."""

    @staticmethod
    def encode(data, *, prefix=None):
        """Encodes data in given dictionary.

        Args:
            data (dict): Dictionary of payload to encode. Values are arrays of numbers.
            prefix (str|None): Optional prefix string.

        Returns:
            Bytes to be sent over the wire.
        """

        elements = []

        if prefix:
            elements.append(prefix)

        for k, v in data.items():
            if v and v[0]:
                # string version of number array:
                vstr = map(lambda i: str(i), v)

                elements.append('({} {})'.format(k, ' '.join(vstr)))

        return ''.join(elements).encode()

    @staticmethod
    def decode(buffer):
        """Decodes network representation of sensor data received from racing server."""
        s = buffer.decode()
        idx_start = s.find('(')
