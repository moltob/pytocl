#
# speedlist.py
#

import numpy as np

class OvertakeListData:
    def __init__(self, factor, start, end):
        self.factor = factor
        self.start = start
        self.end = end

class OvertakeList:
    def __init__(self):
        self.data = np.array([])
        pass

    def add(self, factor, start, end):
        item = OvertakeListData(factor, start, end)
        self.data = np.append(self.data, item)
        #self.data.append([distance, speed])

    def canOvertake(self, distance):
        for i in self.data:
            if distance >= i.start and distance < i.end: #and distance <= distance + (i.end - i.stat) * i.factor:
                return (True, (i.end - distance))
        return False, 0

    def printAll(self):
        for i in self.data:
            print(i)
