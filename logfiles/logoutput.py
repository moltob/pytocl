from pytocl.analysis import DataLogReader

data = DataLogReader(
    '../pytocl/drivelogs/drivelog-2016-10-27-18-46-12.pickle',
    # state_attributes=('angle', 'focused_distances_from_edge'),
    state_attributes=('distance_from_start',),
     command_attributes=('steering',)
).array

for zeile in data:
    print(zeile[1],zeile[2])

print(data[0])

