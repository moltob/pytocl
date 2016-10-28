from pytocl.analysis import DataLogReader
from matplotlib import pyplot as plt

data = DataLogReader(
    '../pytocl/drivelogs/drivelog-2016-10-28-00-24-54.pickle',
    # state_attributes=('angle', 'focused_distances_from_edge'),
    state_attributes=('distance_from_start', 'speed_x', 'wheel_velocities'),
    command_attributes=('accelerator', 'brake')
).array

# 0: zeit, 1: position, 2-5: raddrehzahl, 6: beschleunigung, 7: bremse

for info in data[50:80]:
    print("info: {0}".format([info[2], info[3:7], info[7]]))

#for cycle in data:
#    time = cycle[0]
#    angle = cycle[1]
#    accelerator = cycle[20]
#    brake = cycle[21]

