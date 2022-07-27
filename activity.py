import pandas as pd
import csv

included = set()
techinno = pd.read_csv('/home/elisa/Dropbox/McGill/SCS/Domains/TechInno/Courses/courses.csv',
                       header = None, quoting = csv.QUOTE_NONNUMERIC)
techinno.columns = techinno.iloc[0] 
techinno = techinno[1:]

periods = [ 'W', 'S', 'F' ]
cols = [ 'Code', 'Number', 'Title' ]

for index, record in techinno.iterrows():
    code = record[0]
    number = record[1]
    included.add((code, number))

def process(long):
    period = None
    year = None
    if 'Summer' in long:
        period = 'S'
    elif 'Winter' in long:
        period = 'W'
    elif 'Fall' in long:
        period = 'F'
    else:
        print(f'Invalid study period in {long}')
        quit()
    year = int(long[-4:])
    return period, year

from collections import defaultdict
import re
active = defaultdict(set)

print('Parsing Destiny records of non-credit courses...')
sheet = 0
while True:
    tab = None
    try:
        tab = pd.read_excel('destiny.xls', sheet_name = sheet)
    except:
        break
    sheet += 1
    print(f'Processing sheet {sheet}...')
    counter = 0
    for index, record in tab.iterrows():
        label = str(record[0]).strip().lstrip()
        if label.startswith('Y'):
            status = record[3]
            if status != 'Canceled':
                fields = re.split('\s|-', label)
                assert len(fields) > 1
                code = fields[0]
                number = fields[1]
                section = record[1]
                if '-' in number:
                    parts = number.split('-')
                    number = parts[0]
                course = (code, number)
                (period, year) = process(record[4].strip().lstrip())
                counter += 1
                if course in included:
                    active[course].add((f'{period}{year}', section))
    print(f'Processed {counter} course listings from sheet {sheet} of Destiny')
    
print('Parsing (a lot of) Banner records of credit courses; please be patient...')
tab = None
tab = pd.read_excel('banner.xlsb', engine = 'pyxlsb')
counter = 0
for index, record in tab.iterrows():
    code = record[4]
    number = record[6]
    section = record[7]
    course = (code, number)
    period, year = process(record[2].strip().lstrip())
    counter += 1
    if course in included:
        active[course].add((f'{period}{year}', section))
print(f'Processed {counter} student registrations from Banner')                    

missing = included - set(active.keys())
print(f'{len(missing)} of the requested courses showed no activity in the parsed records')
for (code, number) in missing:
    print(f'{code} {number}')

print('Determining coverage in study periods...')
low = None
high = None
counter = dict()
for course in active:    
    counter[course] = dict()
    for (term, section) in active[course]:
        year = int(term[1:])
        if low is None or year < low:
            low = year
        if high is None or year > high:
            high = year
        if term in counter[course]:
            counter[course][term] += 1 # count the sections
        else:
            counter[course][term] = 1 # first
            
span = []
for year in range(low, high + 1):
    span += [ f'{period}{year}' for period in periods ]

print(f'Producing output of the activations of included courses from {span[0]} to {span[-1]}...')

records = []
for course in active:
    (code, number) = course
    records.append([ code, number ] + [ '{:*^7}'.format(str(counter[course].get(term, ''))) for term in span ])

activity = pd.DataFrame.from_records(records, columns = [ 'Code', 'Number' ] + span)
listing = techinno[cols] # code, number, title (course name)

output = activity.merge(listing, on = [ 'Code', 'Number' ], how = 'outer')
output = output.replace('*' * 7, '') # blanks when no activations
output.to_excel('timeline.xlsx',
                sheet_name = 'Tech-Inno',
                index = False,
                freeze_panes = (1, 2))
            
print('Processing complete :)')
