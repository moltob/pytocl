from pytocl.analysis import DataLogReader
from matplotlib import pyplot  as plt


data = DataLogReader('drivelogs/drivelog-2016-10-27-11-52-02.pickle',state_attributes=( 'angle', 'focused_distances_from_edge'),command_attributes=('steering',)).array


print(data[100][0])

#plt.plot(data)
#plt.show()

fig = plt.figure(figsize=(5, 2))  # initialize figure
ax = fig.add_subplot(3, 2, 2)
#ax.plot(x,y, '-o', c='red', lw=2, label='bla')  # plots a line
ax.plot(data[:][0], data[:][1] , '-o', c='red', label='angle')

fig.show()
plt.show()