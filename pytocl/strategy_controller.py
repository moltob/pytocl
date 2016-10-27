def detect_curve(self, carstate: State):
    m = carstate.distances_from_edge
    if carstate.distances_from_egde_valid and m[9] > 20 and m[9] < 150:
        if m[8] < m[9] < m[10]:
            return 2
        elif m[8] > m[9] > m[10]:
            return 1
        else:
            return 0
    else:
        return 0