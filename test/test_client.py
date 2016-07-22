from unittest import mock

from pytocl.client import Serializer
from pytocl.driver import Driver


def test_init_encoding():
    d = Driver()
    s = Serializer()

    data = {'init': d.range_finder_angles}
    encoded = s.encode(data, prefix='SCR')

    assert encoded == b'SCR(init -90 -75 -60 -45 -30 -20 -15 -10 -5 0 5 10 15 20 30 45 60 75 90)'
