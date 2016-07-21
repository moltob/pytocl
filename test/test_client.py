from unittest import mock

from pytocl.client import Client


def test_driver_assignment():
    client = Client()
    assert not client.driver

    driver = mock.MagicMock()
    client.driver = driver

    assert client.driver is driver
    assert driver.on_connect.called

    client.driver = None

    assert driver.on_disconnect.called
    assert not client.driver
