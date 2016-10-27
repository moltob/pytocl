class PID:
    def __init__(self, k_p, k_i, k_d):
        self.esum = 0
        self.e_alt = 0
        self.k_p = k_p
        self.k_i = k_i
        self.k_d = k_d


    def control(self, ist, soll):
        e = soll - ist
        y_p = self.k_p * e
        self.esum += e
        y_i = self.k_i * self.esum
        y_d = self.k_d * (self.e_alt - e)
        e_alt = e

        y_gesamt = y_p + y_i + y_d

        return y_gesamt

