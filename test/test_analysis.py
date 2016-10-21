import os

import numpy as np
import pytest

from pytocl.analysis import DataLogReader


@pytest.fixture(scope='module', autouse=True)
def working_dir():
    moddir = os.path.dirname(__file__)
    os.chdir(os.path.join(moddir, 'resources'))


def test_data_log_reader_time():
    reader = DataLogReader('drivelog-2016-08-20-17-50-03.pickle')
    a = reader.array

    # only time in retrieved data:
    assert a.shape == (11965, 1)
    assert a[0] == -0.982
    assert a[1] == -0.962
    assert a[100] == 1.044
    assert a[1600] == 33.046
    assert a[10000] == 206.866


def test_data_log_reader():
    reader = DataLogReader('drivelog-2016-08-20-17-50-03.pickle',
                           ('angle', 'wheel_velocities', 'current_lap_time'),
                           ('accelerator', 'steering'))
    a = reader.array

    # only time in retrieved data:
    assert a.shape == (11965, 9)
    assert a[0, 0] == -0.982
    assert a[0, 1] == 0.11095957956283035
    assert all(a[0, 2:6] == np.array((0.0, 0.0, 0.0, 0.0)))
    assert a[0, 6] == -0.982
    assert a[0, 7] == 1
    assert a[0, 8] == 0.61104317802525454
