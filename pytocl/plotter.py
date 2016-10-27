from pytocl.analysis import DataLogReader
from matplotlib import pyplot as plt


def plot():
    data = DataLogReader('drivelogs/drivelog-2016-10-27-12-37-16.pickle',
                         state_attributes=('angle', 'distance_from_center',),
                         command_attributes=('steering',)
                         ).array

    plt.plot(data[:,0], data[:,1])
    plt.show()


if __name__ == '__main__':
    plot()