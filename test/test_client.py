from unittest import mock

from pytocl.client import Serializer, Client, State
from pytocl.driver import Driver


def test_init_encoding():
    d = Driver()
    s = Serializer()

    data = {'init': d.range_finder_angles}
    encoded = s.encode(data, prefix='SCR')

    assert encoded == b'SCR(init -90 -75 -60 -45 -30 -20 -15 -10 -5 0 5 10 15 20 30 45 60 75 90)'


@mock.patch('pytocl.client.socket.socket')
def test_special_messages(mock_socket_ctor):
    mock_socket = mock.MagicMock()
    mock_socket_ctor.return_value = mock_socket
    mock_driver = mock.MagicMock()
    mock_driver.range_finder_angles = Driver().range_finder_angles
    client = Client(driver=mock_driver)
    assert client.state is State.STOPPED

    mock_socket.recvfrom = mock.MagicMock(side_effect=[(b'***identified***', None),
                                                       (b'***restart***', None),
                                                       (b'***shutdown***', None)])

    client.run()
    assert client.state is State.STOPPED

    assert mock_driver.on_restart.call_count == 1
    assert mock_driver.on_shutdown.call_count == 1
