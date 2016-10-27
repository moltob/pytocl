from pytocl.analysis import DataLogReader

data = DataLogReader(
    '../pytocl/drivelogs/drivelog-2016-10-27-15-27-46.pickle',
    # state_attributes=('angle', 'focused_distances_from_edge'),
    state_attributes=('distances_from_edge','opponents'),
     command_attributes=()
).array

for zeile in data:
    print(zeile[0],zeile[1])

print(data[0])

