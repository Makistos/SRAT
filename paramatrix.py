from os.path import isfile, join
from os import listdir
import sys

FIELDS = \
['Div','Date','HomeTeam','AwayTeam','FTHG','FTAG','FTR','Attendance','HS','AS','HST','AST','HHW','AHW','HC','AC''HF','AF','HO','AO','HY','AY','HR','AR']

csv_files = [f for f in listdir("csv") if isfile(join("csv", f)) and f.endswith(".csv")]
print ','.join(FIELDS)
for name in csv_files:
	f = open('csv/' + name)
	l = f.readline()
	header = l.split(',')
	for field in FIELDS:
		if field in header:
			sys.stdout.write('1,')
		else:
			sys.stdout.write('0,')

print
