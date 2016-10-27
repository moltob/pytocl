class PID:
    def __init__(self, kp, kd, ki):
        self.kp, self.kd, self.ki = kp, kd, ki
        self.last_e = None
        self.last_es = []

    def get_action(self, e):
        if self.last_e is None:
            self.last_e = e

        self.last_es.append(e)
        if len(self.last_es) > 20:
            self.last_es.pop(0)

        de = e - self.last_e
        ie = sum(self.last_es)

        self.last_e = e
        out = -self.kp*e - self.kd*de - self.ki*ie

        return out
