from pytocl.analysis import DataLogReader
from matplotlib import pyplot  as plt
from pytocl.log_utils import *

drivelog = get_newest_drivelog()
data = DataLogReader(drivelog,state_attributes=( 'angle','distance_from_center', 'distance_from_start', 'focused_distances_from_edge'),command_attributes=('steering',)).array

print(drivelog)

#print(data)
print(data[0])
print(data[1])
print(data[0][0])
print(data[1][0])
print(data[:, 0])

#plt.plot(data[:, 0],data[:, 1])

#plt.show()

fig = plt.figure(figsize=(5, 2))  # initialize figure
angle = fig.add_subplot(1,2,1)
#ax.plot(x,y, '-o', c='red', lw=2, label='bla')  # plots a line
angle.plot(data[:, 0],data[:, 1] , c='red', label='angle')
#distance = fig.add_subplot(1,2,2)
#distance.plot(data[:, 0],data[:, 2] , c='green', label='angle')

startDistance = fig.add_subplot(1,2,2)
startDistance.plot(data[:, 0],data[:, 3] , c='green', label='angle')
#angle.plot(data[:, 0],data[:, 3] , c='green', label='angle')

fig.show()
plt.show()