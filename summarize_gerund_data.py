from os.path import isfile
from sys import argv

if not isfile(argv[1]) or not isfile(argv[2]):
    print("Please provide an input and an output file path as CL arguments.")
    exit(1)

with open(argv[1], 'r') as fh:
    csv_content = fh.readlines()

abbrev_to_author_name = {
        'HP1' : 'Peter Heylyn',
        'PW1' : 'William Prynne',
        'FT1' : 'Thomas Fuller',
        'MJ1' : 'John Milton',
        'TJ1' : 'Jeremy Taylor',
        'BRG2': 'Roger Boyle',
        'PT2' : 'Thomas Pierce',
        'FG2' : 'George Fox',
        'BRB2': 'Robert Boyle',
        'SG2' : 'George Swinnock',
        'BJ2' : 'John Bunyan',
        'FJ2' : 'John Flavell',
        'TJ2' : 'John Tillotson',
        'DJ2' : 'John Dryden',
        'MI3' : 'Increase Mather',
        'CN3' : 'Nathaniel Crouch',
        'BA3' : 'Aphra Behn',
        'BG3' : 'Gilbert Burnet',
        'PW3' : 'William Penn'
}

output = [ ['author', 'year', 'ng', 'vg'] ]
current_author_current_year = (None, None)
for csv_line in csv_content[1:]:
    csv_line_parsed = csv_line.split(',')
    if current_author_current_year != (csv_line_parsed[0], csv_line_parsed[1]):
        if current_author_current_year != (None, None):
            new_record = (abbrev_to_author_name[current_author_current_year[0]], current_author_current_year[1], ng_count, vg_count)
            output.append(new_record)
        current_author_current_year = (csv_line_parsed[0], csv_line_parsed[1])
        ng_count = 0
        vg_count = 0
    if csv_line_parsed[3] == 'NG':
        ng_count += 1
    elif csv_line_parsed[3] == 'VG':
        vg_count += 1
    else:
        assert False
new_record = (abbrev_to_author_name[current_author_current_year[0]], current_author_current_year[1], ng_count, vg_count)
output.append(new_record)

csv_output = '\n'.join(map(lambda record: ','.join(map(str, record)), output))

with open(argv[2], 'w') as fh:
    fh.write(csv_output)
