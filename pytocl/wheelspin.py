from pytocl.car import State

class WheelSpin:
    def __init__(self):
        pass

    def slipFactor(self, carstate: State):
        wheels = carstate.wheel_velocities
        front = wheels[0] + wheels[1]
        rear = wheels[2] + wheels[3]
        return front / rear if rear > 0.01 else 1

    def blockingFactor(self, carstate: State):
        wheels = carstate.wheel_velocities
        front = wheels[0] + wheels[1]
        rear = wheels[2] + wheels[3]
        return front / rear if rear > 0.01 else 1
