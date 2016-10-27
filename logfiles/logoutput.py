from pytocl.analysis import DataLogReader
from matplotlib import pyplot as plt

data = DataLogReader(
    '../pytocl/drivelogs/drivelog-2016-10-28-00-24-54.pickle',
    # state_attributes=('angle', 'focused_distances_from_edge'),
    state_attributes=('angle', 'distances_from_edge'),
    command_attributes=('accelerator', 'brake')
).array

print(len(data[0]))

plt.plot(data[:,0], data[:,21])
plt.xlabel('time')
plt.ylabel('angle')

#for cycle in data:
#    time = cycle[0]
#    angle = cycle[1]
#    accelerator = cycle[20]
#    brake = cycle[21]

