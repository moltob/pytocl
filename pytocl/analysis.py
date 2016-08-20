"""Utilities to evaluate car and driver behavior."""
import datetime
import logging
import os
import pickle

import itertools

import numpy as np

_logger = logging.getLogger(__name__)


class DataLogWriter:
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
            self.pickler.dump((state, command))
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


class DataLogReader:
    """Deserialization of logged data as ``np.array``."""

    def __init__(self, filepath, state_attributes=None, command_attributes=None):
        self.filepath = filepath
        self.state_attributes = state_attributes or []
        self.command_attributes = command_attributes or []

        self._current_lap_time = 0
        self._last_laps_accumulated_time = 0
        self._numrows = 0

    @property
    def overall_time(self):
        return self._current_lap_time + self._last_laps_accumulated_time

    @property
    def array(self):
        self._current_lap_time = float('-inf')
        self._last_laps_accumulated_time = 0
        self._numrows = 0

        _logger.info('Accessing data log {}.'.format(self.filepath))
        with open(self.filepath, 'rb') as logfile:
            unpickler = pickle.Unpickler(logfile)
            rows = self.rows(unpickler)
            a = np.fromiter(itertools.chain.from_iterable(rows), float)
            a.resize((self._numrows, a.size / self._numrows))

            return a

    def rows(self, unpickler):
        """Iterates over rows in data."""
        try:
            while True:
                state, command = unpickler.load()

                # compute accumulated race time:
                if self._current_lap_time > state.current_lap_time:
                    self._last_laps_accumulated_time += state.last_lap_time
                self._current_lap_time = state.current_lap_time

                row = itertools.chain((self.overall_time,),
                                      state.chain(*self.state_attributes),
                                      command.chain(*self.command_attributes))
                self._numrows += 1

                yield row
        except EOFError:
            pass
