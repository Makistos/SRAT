__author__ = 'mep'

import csv
import pprint

f = open('PL2012-2013.csv', 'r')

reader = csv.DictReader(f)

matches = []

for line in reader:
    matches.append(line)

pprint.pprint(matches)
