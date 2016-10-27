from pytocl.analysis import DataLogReader

data = DataLogReader(
    '../pytocl/drivelogs/drivelog-2016-10-27-14--57.pickle',
    # state_attributes=('angle', 'focused_distances_from_edge'),
    state_attributes=('distances_from_edge','opponents'),
     command_attributes=()
).array

for zeile in data:
    print(zeile[0],zeile[1])38

print(data[0])

