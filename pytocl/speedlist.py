#
# speedlist.py
#

import numpy as np

class SpeedList:

    def __init__(self):
        self.data = list()
        pass

    def add(self, distance, speed):
        #print (distance, speed)
        self.data = np.append(self.data, [distance, speed])
        #self.data.append([distance, speed])

    def printAll(self):
        for i in self.data:
            print(i)
