from pytocl.driver import Driver


def test_pid():
    d = Driver()

    for ist in range(200):
        y = d.pid(ist, 100)
        print(y)

    assert True


