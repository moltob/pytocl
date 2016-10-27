from pytocl.driver import Driver

def test_direction_with_biggest_distances():
    d = Driver()
    d.directions = -90, -45, 0, 45, 90

    dir_biggest_dist = d.direction_with_biggest_distance((100, 100, 100, 200, 100))
    assert dir_biggest_dist == 45