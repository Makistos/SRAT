__author__ = 'mep'

import csv
import pprint
from datetime import datetime
from os import listdir
from os.path import isfile, join

csvFiles = [ f for f in listdir("csv") if isfile(join("csv", f))]

print "Using files: " + str((csvFiles))

matchFiles = {}

for c in csvFiles:
    matchFiles[(c[0:2], c[2:6])] = c

pprint.pprint(matchFiles)
def fieldAvg(l, fieldName):
    return sum([float(line[fieldName]) for line in l]) / len(l)


def fieldSum(l, fieldName):
    return sum(line[fieldName] for line in l)


def fieldCount(l, fieldName, value):
    return len([line for line in l if line[fieldName] == value])


def filterRows(l, fieldName, value):
    return [line for line in l if line[fieldName] == value]


def listTeamMatchesBefore(l, date, team, num):
    #retval = [m for m in l if (m["HomeTeam"] == team or m["AwayTeam"] == team)]
    retval = [m for m in l if datetime.strptime(m['Date'], '%d/%m/%y') < datetime.strptime(date, '%d/%m/%y') and (m['HomeTeam'] == team or m['AwayTeam'] == team)]
    return retval

matches = {}

for ((key1, key2), name) in matchFiles.iteritems():
    f = open('csv/' + name)
    matches[(key1, key2)] = []
    reader = csv.DictReader(f)
    for line in reader:
        matches[(key1, key2)].append(line)
    f.close()

#days = [match["Date"] for match in matches[("E0", "2012")]]
#print days

#print sum([float(match["FTHG"]) for match in matches]) / len(matches)
print "Average goals (home): " + str(fieldAvg(matches[("E0", "2012")], "FTHG"))
print "Average goals (away): " + str(fieldAvg(matches[("E0", "2012")], "FTAG"))
print "Home wins: " + str("%.2f" % (float(fieldCount(matches[("E0", "2012")], "FTR", "H")) / len(matches[("E0", "2012")]) * 100))
print "Draws: " + str("%.2f" % (float(fieldCount(matches[("E0", "2012")], "FTR", "A")) / len(matches[("E0", "2012")]) * 100))
print "Away wins: " + str("%.2f" % (float(fieldCount(matches[("E0", "2012")], "FTR", "D")) / len(matches[("E0", "2012")]) * 100))

print fieldCount(filterRows(matches[("E0", "2012")], "HomeTeam", "Everton"), "FTR", "H")
print fieldCount(filterRows(matches[("E0", "2012")], "HomeTeam", "Everton"), "FTR", "A")
print fieldCount(filterRows(matches[("E0", "2012")], "HomeTeam", "Everton"), "FTR", "D")
e = listTeamMatchesBefore(matches[("E0", "2012")], '23/03/14', 'Everton', 6)
print "All matches for season 2012 (" + str(len(e)) + ")"
for m in e:
    print m["Date"] + ": " + m["HomeTeam"] + "-" + m["AwayTeam"]

# Search for home matches for team in entire database
# Find all matches for E0
m = [value for (key,value) in matches.iteritems() if key[0] == 'E0']
# Need to flatten the list first
m2 = [item for sublist in m for item in sublist]
e = filterRows(m2, "HomeTeam", "Everton")
print
print "All home matches (" + str(len(e)) + ")"
for m in e:
    print m["Date"] + ": " + m["HomeTeam"] + " " + m["FTHG"] + "-" + m["AwayTeam"] + " " + m["FTAG"]

# Calculate number of home wins for team
print "Home wins for team in database: " + str(fieldCount(filterRows(m2, "HomeTeam", "Everton"), "FTR", "H"))
