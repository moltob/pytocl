#
# speedlist.py
#

import numpy as np

class SpeedListData:
    def __init__(self, distance, speed):
        self.distance = distance
        self.speed = speed

class SpeedList:
    def __init__(self):
        self.data = list()
        pass

    def add(self, distance, speed):
        item = SpeedListData(distance, speed)
        self.data = np.append(self.data, item)
        #self.data.append([distance, speed])

    def getSpeedForDistance(self, distance):
        index = 0
        findex = -1
        for i in self.data:
            #print(i.distance)
            if distance < i.distance:
                findex = index-1
                break
            index += 1
        #print(findex)
        return self.data[findex].speed

    def printAll(self):
        for i in self.data:
            print(i)
