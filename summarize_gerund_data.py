from os.path import isfile
from sys import argv

if not isfile(argv[1]) or not isfile(argv[2]):
    print("Please provide an input and an output file path as CL arguments.")
    exit(1)

with open(argv[1], 'r') as fh:
    csv_content = fh.readlines()

output = []
current_author_current_year = (None, None)
for csv_line in csv_content[1:]:
    csv_line_parsed = csv_line.split(',')
    if current_author_current_year != (csv_line_parsed[0], csv_line_parsed[1]):
        if current_author_current_year != (None, None):
            output.append((current_author_current_year[0], current_author_current_year[1], ng_count, vg_count))
        current_author_current_year = (csv_line_parsed[0], csv_line_parsed[1])
        ng_count = 0
        vg_count = 0
    if csv_line_parsed[3] == 'NG':
        ng_count += 1
    elif csv_line_parsed[3] == 'VG':
        vg_count += 1
    else:
        assert False
output.append((current_author_current_year[0], current_author_current_year[1], ng_count, vg_count))

csv_output = '\n'.join(map(lambda record: ','.join(map(str, record)), output))

with open(argv[2], 'w') as fh:
    fh.write(csv_output)
