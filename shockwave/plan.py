class Plan:
    def __init__(self, strategy):
        self.strategy = strategy

    def get_desired_position(self):
        return 0

    def get_desired_speed(self):
        return 15

    def get_desired_angle(self):
        return 0

    def get_desired_focus(self):
        return 0