"""Utilities to evaluate car and driver behavior."""
import datetime
import logging
import os
import pickle

_logger = logging.getLogger(__name__)


class Snapshot:
    """Container for pair consisting of (input) car state and (output) drive command.

    This container provides a single object used for serialization of during the race. It later
    can be loaded again to analyze how the driver responded to certain input data.
    """

    def __init__(self, state, command):
        self.state = state
        self.command = command


class DataLogger:
    """Serialization of snapshots."""

    def __init__(self):
        dirname = 'drivelogs'
        timestr = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        fname = 'drivelog-{}.pickle'.format(timestr)
        fpath = os.path.abspath(os.path.join(dirname, fname))
        _logger.info('Logging data snapshots to {}.'.format(fpath))

        os.makedirs(dirname, exist_ok=True)
        self.file = open(fpath, 'wb')
        self.pickler = pickle.Pickler(self.file)
        self.numlogged = 0

    def __del__(self):
        """Try to save data before instance is destroyed."""
        self.close()

    def log(self, state, command):
        """Log pair of data."""
        if self.logging:
            self.pickler.dump(Snapshot(state, command))
            self.numlogged += 1
        else:
            _logger.warning('Logger closed, cannot log data to file.')

    def close(self):
        """End logging by closing the associated file."""
        if self.logging:
            self.file.close()
            _logger.info('Saved {} log entries.'.format(self.numlogged))
            self.file = None
            self.pickler = None
            self.numlogged = 0

    @property
    def logging(self):
        return self.file is not None
