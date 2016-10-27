from pytocl.analysis import DataLogReader
from matplotlib import pyplot as plt

data = DataLogReader(
    'C:\TG\hackathon\project\jazz\pytocl\drivelogs\drivelog-2016-10-27-20-22-32.pickle',
    state_attributes=('angle',),
    command_attributes=('steering',)
).array

plt.figure(1)
plt.subplot(211)
plt.plot(data[:,0], data[:, 1],data[:,0], data[:,2]*21, 'bo')
plt.xlabel('time [s]')
plt.ylabel('Steering angle*21 [deg]')

plt.subplot(212)
plt.plot(data[:,0], data[:, 1],data[:,0], data[:,2],'bo')
plt.xlabel('time [s]')
plt.ylabel('Steering angle [deg]')
plt.show()