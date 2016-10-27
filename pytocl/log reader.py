from pytocl.analysis import DataLogReader
from matplotlib import pyplot  as plt
from pytocl.log_utils import *

drivelog = get_newest_drivelog()
data = DataLogReader(drivelog,state_attributes=( 'angle','distance_from_center', 'distance_from_start', 'wheel_velocities', 'speed_x',  'focused_distances_from_edge'),command_attributes=('steering',)).array

print(drivelog)

#print(data)
print(data[0])
print(data[:, 0])


#plt.plot(data[:, 0],data[:, 1])

#plt.show()

fig = plt.figure(figsize=(5, 2))  # initialize figure
angle = fig.add_subplot(1,2,1)

data[:, 8] = data[:, 8] * 3.6

#ax.plot(x,y, '-o', c='red', lw=2, label='bla')  # plots a line
angle.plot(data[:, 0],data[:, 8] , c='red', label='globalSpeed')
#distance = fig.add_subplot(1,2,2)
#distance.plot(data[:, 0],data[:, 2] , c='green', label='angle')

startDistance = fig.add_subplot(1,2,2)
startDistance.plot(data[:, 0],data[:, 4] , c='green', label='wheel1')
startDistance.plot(data[:, 0],data[:, 5] , c='red',  label='wheel2')
startDistance.plot(data[:, 0],data[:, 6] , c='yellow', label='wheel3')
startDistance.plot(data[:, 0],data[:, 7] , c='blue', label='wheel4')

#angle.plot(data[:, 0],data[:, 3] , c='green', label='angle')

fig.show()
plt.show()