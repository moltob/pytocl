class LowPass:
    def __init__(self, factor, iv):
        self.value = iv
        self.P = factor

    def filter(self, value):
        self.value += (value - self.value) * self.P
        return self.value