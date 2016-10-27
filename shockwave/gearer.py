from pytocl.car import State


class Gearer:
    def __init__(self, plan):
        self.plan = plan

    def get_gear(self, state: State):
        return 2 # -1 to 6