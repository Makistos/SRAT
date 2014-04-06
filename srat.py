__author__ = 'mep'

import csv
from pprint import pprint
from datetime import datetime
from os import listdir
from os.path import isfile, join
import re
from elo import elo_adjust

#import itertools as IT
#import collections

matches = {}
matchFiles = {}
seasonStatsDict = {}

# Extract some keys from a dict (the whole match dict is very big, this helps debugging)
extractDict = lambda keys, dict: reduce(lambda x, y: x.update({y[0]:y[1]}) or x,
                                    map(None, keys, map(dict.get, keys)), {})


def flatten_list():
    pass


def flatten_dict(m):
    tmp = []
    for ((key1, key2), value) in m.iteritems():
        tmp.append(value)

    # Flatten lists:
    ret = []
    ret = [item for sublist in tmp for item in sublist]
    return ret

#    iterable = iter(iterable)
#    remainder = iterable
#    while True:
#        first = next(remainder)
#        if isinstance(first, ltypes) and not isinstance(first, basestring):
#            remainder = IT.chain(first, remainder)
#            first = next(iter(first))
#        else:
#            yield first


def open_files(files):
    """
      Open csv files (and .csv$ only)
    """
    if (files == ''):
        csvFiles = [f for f in listdir("csv") if isfile(join("csv", f)) and f.endswith(".csv")]
    else:
        csvFiles = files

    print "Using files: " + str((csvFiles))

    for c in csvFiles:
        matchObj = re.match(r'(.+)(\d{4})\-(\d{4})(.*)', c)
        matchFiles[(matchObj.group(1), matchObj.group(2))] = c


def field_avg(lst, fieldName):
    retval = 0.0
    s = 0
    try:
        for line in lst:
            s += float(line[fieldName])
#        retval = sum([float(line[fieldName]) for line in lst]) / len(l)
    except ValueError:
        print "ValueError! Value for " + fieldName + " is: " + str(line[fieldName])
        #print line
#        print "HomeTeam: " + str(line["HomeTeam"]) + ", AwayTeam: " + str(line["AwayTeam"])
        retval = 0.0
    retval = s / len(l)
    return retval


def field_sum(l, fieldName):
    return sum(line[fieldName] for line in l)


def field_count(l, fieldName, value):
    return len([line for line in l if line[fieldName] == value])


def filter_rows(l, fieldName, value):
    return [line for line in l if line[fieldName] == value]


def list_team_matches_before(l, date, team, num):
    #retval = [m for m in l if (m["HomeTeam"] == team or m["AwayTeam"] == team)]
    retval = [m for m in l if datetime.strptime(m['Date'], '%d/%m/%y') < datetime.strptime(date, '%d/%m/%y') and (m['HomeTeam'] == team or m['AwayTeam'] == team)]
    return retval


def season_stats(l):
    flagThis = 0
    for (key, season) in l.iteritems():
        key2 = key + ('HWIN',)
        try:
            seasonStatsDict[key2] = str("%.2f" % (float(field_count(season, "FTR", "H")) / len(season) * 100))
        except ZeroDivisionError:
            print "Division by zero: " + str(key2)
        key2 = key + ('AWIN',)
        seasonStatsDict[key2] = str("%.2f" % (float(field_count(season, "FTR", "A")) / len(season) * 100))
        key2 = key + ('DRAW',)
        seasonStatsDict[key2] = str("%.2f" % (float(field_count(season, "FTR", "D")) / len(season) * 100))
        key2 = key + ('HGOALS',)
        seasonStatsDict[key2] = str(field_avg(season, "FTHG"))
        key2 = key + ('AGOALS',)
        seasonStatsDict[key2] = str(field_avg(season, "FTAG"))


def home_match_stats(m, record):
    retval = record

    if m["FTR"] == 'H':
        retval["Wins"] = record["Wins"] + 1
    elif m["FTR"] == 'D':
        retval["Draws"] = record["Draws"] + 1
    else:
        retval["Losses"] = record["Losses"] + 1

    retval["FTHG"] = int(m["FTHG"]) + int(record["FTHG"])
    retval["FTAG"] = int(m["FTAG"]) + int(record["FTAG"])

    return retval

def away_match_stats(m, record):
    retval = record

    if m["FTR"] == 'A':
        retval["Wins"] = record["Wins"] + 1
    elif m["FTR"] == 'D':
        retval["Draws"] = record["Draws"] + 1
    else:
        retval["Losses"] = record["Losses"] + 1

    retval["FTHG"] = int(m["FTHG"]) + int(record["FTHG"])
    retval["FTAG"] = int(m["FTAG"]) + int(record["FTAG"])

    return retval

def versus_team(l, team):
    """
    @rtype : dict
    @param l: List of matches (single team) to create the table
    @param team: Team name
    @return: Dict containing the data. Key is ("opponent", "away"|"home) and
             value is {"Wins": x, "Draws": x, "Losses": x, "FTHG": x, "FTAG": x
    """
    retval = {}
    homeList = [v for v in l if v["HomeTeam"] == team]
    awayList = [v for v in l if v["AwayTeam"] == team]

    for match in homeList:
        awayTeam = match["AwayTeam"]
        if (awayTeam, "home") not in retval:
            retval[(awayTeam, "home")] = {"Wins": 0, "Draws": 0, "Losses": 0, "FTHG": 0, "FTAG":0 }
        retval[(awayTeam, "home")] = home_match_stats(match, retval[(awayTeam, "home")])
    for match in awayList:
        homeTeam = match["HomeTeam"]
        if (homeTeam, "away") not in retval:
            retval[(homeTeam, "away")] = {"Wins": 0, "Draws": 0, "Losses": 0, "FTHG": 0, "FTAG":0 }
        retval[(homeTeam, "away")] = away_match_stats(match, retval[(homeTeam, "away")])
    return {team: retval}


if __name__ == '__main__':
    open_files("")

    for ((key1, key2), name) in matchFiles.iteritems():
        f = open('csv/' + name)
        matches[(key1, key2)] = []
        reader = csv.DictReader(f)
        for line in reader:
            # Make the dict a bit shorter, at least for now
            shortDict = extractDict(['Date', 'HomeTeam', 'AwayTeam', 'FTR', 'FTHG', 'FTAG'], line)
            matches[(key1, key2)].append(shortDict)
        f.close()

    #for match in matches[("E0", "2010")]:
    #    pprint(shortDict)

    l = flatten_dict(matches)
    #print "Tot: " + str(len(l))

    # Get list items in a flat list
    E0 = [v for (k,v) in matches.iteritems() if k[0] == 'E0']
    l2 = [item for sublist in E0 for item in sublist]

    #with open('test.csv', 'wt') as out:
    #    pprint(l2, stream=out)
    #print "E0 tot: " + str(len(l2))
    #with open('test.csv', 'wt') as out:
    #    pprint(matches, stream=out)

    print "Stats for entire data set: "
    season_stats(matches)

    tmp = [v for (k,v) in matches.iteritems() if k[0] == 'E0']
    #pprint(tmp)
    #print "len: " + str(len(tmp))
    #versusTable = versusTeam([v for (k,v) in matches.iteritems() if k[0] == 'E0'], "Everton")
    #pprint(l2)
    seen = ()
    tmp = []
    tmp = [x["HomeTeam"] for x in l2]
    teams = []
    teams = sorted(list(set(tmp)))
#    print str(teams)
    versusTable = map(lambda x: versus_team(l2, x), teams)
#    pprint(versusTable)

    for i in range(len(l2)):
        match = list(l2)[i]
#        print match
        tmp = [x for x in l2[0:i-1] if x["HomeTeam"] == match["HomeTeam"]]
        if len(tmp) < 1:
            old_home = 1000
        elif "home_elo" in tmp[-1]:
            old_home = tmp[-1]["home_elo"]
        else:
            old_home = 1000
        tmp = [x for x in l2[0:i-1] if x["AwayTeam"] == match["AwayTeam"]]
        if len(tmp) < 1:
            old_home = 1000
        elif "away_elo" in tmp[-1]:
            old_away = tmp[-1]["away_elo"]
        else:
            old_away = 1000

        (new_home, new_away) = elo_adjust(match, old_home, old_away)
        match["home_elo"] = old_home + new_home
        match["away_elo"] = old_away + new_away
        print match

        print ("%s: %s (%d -> %d) %d - %d %s (%d -> %d)" % (match["Date"],
            match["HomeTeam"],
            float(round(old_home, 2)),
            float(round(match["home_elo"],2)),
            int(match["FTHG"]),
            int(match["FTAG"]),
            match["AwayTeam"],
            float(round(old_away, 2)),
            float(round(match["away_elo"], 2))))

    #pprint(seasonStatsDict)
    #print sum([float(match["FTHG"]) for match in matches]) / len(matches)
    #print fieldCount(filterRows(matches[("E0", "2012")], "HomeTeam", "Everton"), "FTR", "H")
    #print fieldCount(filterRows(matches[("E0", "2012")], "HomeTeam", "Everton"), "FTR", "A")
    #print fieldCount(filterRows(matches[("E0", "2012")], "HomeTeam", "Everton"), "FTR", "D")
    #e = listTeamMatchesBefore(matches[("E0", "2012")], '23/03/14', 'Everton', 6)
    #print "All matches for season 2012 (" + str(len(e)) + ")"
    #for m in e:
    #    print m["Date"] + ": " + m["HomeTeam"] + "-" + m["AwayTeam"]
    #
    ## Calculate number of home wins for team
    #print "Home wins for team in database: " + str(fieldCount(filterRows(m2, "HomeTeam", "Everton"), "FTR", "H"))
