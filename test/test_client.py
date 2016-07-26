from unittest import mock

from pytocl.client import Serializer, Client, State
from pytocl.driver import Driver


def test_init_encoding():
    d = Driver()
    s = Serializer()

    data = {'init': d.range_finder_angles}
    encoded = s.encode(data, prefix='SCR')

    assert encoded == b'SCR(init -90 -75 -60 -45 -30 -20 -15 -10 -5 0 5 10 15 20 30 45 60 75 90)'


def test_decode_server_message():
    buffer = b'(angle 0.008838)' \
             b'(curLapTime 4.052)' \
             b'(damage 0)' \
             b'(distFromStart 1015.56)' \
             b'(distRaced 42.6238)' \
             b'(fuel 93.9356)' \
             b'(gear 3)' \
             b'(lastLapTime 0)' \
             b'(opponents 200 200 200 200 200 200 200 200 200 200 200 200 200 200 200 200 200 200' \
             b' 200 200 200 200 200 200 200 200 200 200 200 200 200 200 200 200 200 200)' \
             b'(racePos 1)' \
             b'(rpm 4509.31)' \
             b'(speedX 81.5135)' \
             b'(speedY 0.40771)' \
             b'(speedZ -2.4422)' \
             b'(track 4.3701 4.52608 5.02757 6.07753 8.25773 11.1429 13.451 16.712 21.5022' \
             b' 30.2855 51.8667 185.376 69.9077 26.6353 12.6621 8.2019 6.5479 5.82979 5.63029)' \
             b'(trackPos 0.126012)' \
             b'(wheelSpinVel 67.9393 68.8267 71.4009 71.7363)' \
             b'(z 0.336726)' \
             b'(focus 26.0077 27.9798 30.2855 33.0162 36.3006)'

    d = Serializer().decode(buffer)

    assert len(d) == 19
    assert d['angle'] == '0.008838'
    assert d['wheelSpinVel'] == ['67.9393', '68.8267', '71.4009', '71.7363']


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
