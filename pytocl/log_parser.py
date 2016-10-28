from pytocl.analysis import DataLogReader

import argparse


def list_length(l):
    if l:
        return 1 + list_length(l[1:])
    return 0

parser = argparse.ArgumentParser(description='Parsing of pytocl logs.')
parser.add_argument('-i', '--input', help='raw data log in pickle format.', required=True)
parser.add_argument('-o', '--output', help='parsed log file in table format.', required=True)
parser.add_argument('-sa', '--state_attributes', help='state attributes to parse', nargs='*')
parser.add_argument('-ca', '--command_attributes', help='command attributes to parse', nargs='*')
parser.add_argument('-cda', '--custom_data_attributes', help='custom data attributes to parse', nargs='*')

args = parser.parse_args()
state_attributes = args.state_attributes or []
command_attributes = args.command_attributes or []
custom_data_attributes = args.custom_data_attributes or []

data = DataLogReader(args.input, state_attributes=state_attributes, command_attributes=command_attributes, custom_data_attributes=custom_data_attributes).array

with open(args.output, 'wt') as target_file:
    header_length = list_length(state_attributes + command_attributes + custom_data_attributes)
    line_attrib = ['time'] + state_attributes + command_attributes + custom_data_attributes
    header_format = '{}' + '{:>25}' * (header_length) + '\n'
    header = header_format.format(*line_attrib)

    target_file.write(header)
    for data_line in data:
        data_str = [str(data_element) for data_element in data_line]
        data_length = len([*data_line])
        data_format = '{}' + '{:>25}' * (data_length - 1) + '\n'
        line = data_format.format(*data_str)

        # line = ';'.join([str(value) for value in i]) + '\n'
        target_file.write(line)

pass
