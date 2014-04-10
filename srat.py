__author__ = 'mep'

import csv
from pprint import pprint
from datetime import datetime
from os import listdir
from os.path import isfile, join
import re
from elo import elo_calculate
import db

#import itertools as IT
#import collections

FIELDS = [db.DATE, db.HOME_TEAM, db.AWAY_TEAM, db.FTR, db.FTHG, db.FTAG]
FORM_TABLE = [2, 4, 6, 10, 15]  # Match lengths to which calculate the form parameters
DATE_FORMAT = '%y/%m/%d'
matches = {}
matchFiles = {}
seasonStatsDict = {}

# Extract some keys from a dict (the whole match dict is very big, this helps debugging)
extractDict = lambda keys, dict: reduce(lambda x, y: x.update({y[0]: y[1]}) or x,
                                        map(None, keys, map(dict.get, keys)), {})

flatten_dict = lambda d: [item for sublist in d.itervalues() for item in sublist]
filter_rows = lambda li, field, value: [line for line in li if line[field] == value]
field_sum = lambda li, field: sum(float(line[field]) for line in li)
field_count = lambda li, field, value: len([line for line in li if line[field] == value])
team_matches_home = lambda li, team: [m for m in li if m[db.HOME_TEAM] == team]
team_matches_away = lambda li, team: [m for m in li if m[db.AWAY_TEAM] == team]
team_matches = lambda li, team: team_matches_home(li, team) + team_matches_away(li, team)
list_nmatches_before = \
    lambda li, date, c: [m for m in li
                               if datetime.strptime(m[db.DATE], DATE_FORMAT) < datetime.strptime(date, DATE_FORMAT)][-c:]
list_matches_before = \
    lambda li, date: [m for m in li
                         if datetime.strptime(m[db.DATE], DATE_FORMAT) < datetime.strptime(date, DATE_FORMAT)]
list_matches_after = \
    lambda li, date: [m for m in li
                         if datetime.strptime(m[db.DATE], DATE_FORMAT) > datetime.strptime(date, DATE_FORMAT)]

#def field_avg(lst, field):
#    s = 0
#    for line in lst:
#        if isinstance(float(line[field]), float):
#            s += float(line[field])
#    retval = s / len(lst)
#    return retval
#
field_avg = lambda li, field: sum([float(line[field]) for line in li if isinstance(float(line[field]), float)]) / \
                              len([1 for line in li if isinstance(float(line[field]), float)])

def print_matches(match_list):
    for match in match_list:
        print("%s: (%d->%d) %s %d - %d %s (%d->%d)" %
              (match[db.DATE],
               round(float(match[db.HE]) - float(match[db.HEC]), 2),
               round(float(match[db.HE]), 2),
               match[db.HOME_TEAM],
               int(match[db.FTHG]),
               int(match[db.FTAG]),
               match[db.AWAY_TEAM],
               round(float(match[db.AE]) - float(match[db.AEC]), 2),
               round(float(match[db.AE]), 2)))


def flatten_list():
    pass


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

    for ((key1, key2), name) in matchFiles.iteritems():
        f = open('csv/' + name)
        matches[(key1, key2)] = []
        reader = csv.DictReader(f)
        for line in reader:
            # Make the dict a bit shorter, at least for now
            shortDict = extractDict(FIELDS, line)
            if shortDict[db.DATE] == '':
                continue
            try:
                shortDict[db.DATE] = datetime.strptime(shortDict[db.DATE], '%d/%m/%y').strftime(DATE_FORMAT)
            except:
                shortDict[db.DATE] = datetime.strptime(shortDict[db.DATE], '%d/%m/%Y').strftime(DATE_FORMAT)

            matches[(key1, key2)].append(shortDict)
        f.close()




def season_stats(l):
    flagThis = 0
    for (key, season) in l.iteritems():
        key2 = key + ('HWIN',)
        try:
            seasonStatsDict[key2] = str("%.2f" % (float(field_count(season, db.FTR, "H")) / len(season) * 100))
        except ZeroDivisionError:
            print "Division by zero: " + str(key2)
        key2 = key + ('AWIN',)
        seasonStatsDict[key2] = str("%.2f" % (float(field_count(season, db.FTR, "A")) / len(season) * 100))
        key2 = key + ('DRAW',)
        seasonStatsDict[key2] = str("%.2f" % (float(field_count(season, db.FTR, "D")) / len(season) * 100))
        key2 = key + ('HGOALS',)
        seasonStatsDict[key2] = str(field_avg(season, db.FTHG))
        key2 = key + ('AGOALS',)
        seasonStatsDict[key2] = str(field_avg(season, db.FTAG))


def home_match_stats(m, record):
    retval = record

    if m[db.FTR] == 'H':
        retval["Wins"] = record["Wins"] + 1
    elif m[db.FTR] == 'D':
        retval["Draws"] = record["Draws"] + 1
    else:
        retval["Losses"] = record["Losses"] + 1

    retval[db.FTHG] = int(m[db.FTHG]) + int(record[db.FTHG])
    retval[db.FTAG] = int(m[db.FTAG]) + int(record[db.FTAG])

    return retval


def away_match_stats(m, record):
    retval = record

    if m[db.FTR] == 'A':
        retval["Wins"] = record["Wins"] + 1
    elif m[db.FTR] == 'D':
        retval["Draws"] = record["Draws"] + 1
    else:
        retval["Losses"] = record["Losses"] + 1

    retval[db.FTHG] = int(m[db.FTHG]) + int(record[db.FTHG])
    retval[db.FTAG] = int(m[db.FTAG]) + int(record[db.FTAG])

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
    homeList = [v for v in l if v[db.HOME_TEAM] == team]
    awayList = [v for v in l if v[db.AWAY_TEAM] == team]

    for match in homeList:
        awayTeam = match[db.AWAY_TEAM]
        if (awayTeam, "home") not in retval:
            retval[(awayTeam, "home")] = {"Wins": 0, "Draws": 0, "Losses": 0, db.FTHG: 0, db.FTAG: 0}
        retval[(awayTeam, "home")] = home_match_stats(match, retval[(awayTeam, "home")])
    for match in awayList:
        homeTeam = match[db.HOME_TEAM]
        if (homeTeam, "away") not in retval:
            retval[(homeTeam, "away")] = {"Wins": 0, "Draws": 0, "Losses": 0, db.FTHG: 0, db.FTAG: 0}
        retval[(homeTeam, "away")] = away_match_stats(match, retval[(homeTeam, "away")])
    return {team: retval}


if __name__ == '__main__':
    #open_files("")
    open_files(["E02013-2014.csv"])

    l = flatten_dict(matches)

    # Get list items in a flat list
    E0 = [v for (k, v) in matches.iteritems() if k[0] == 'E0']
    l2 = sorted([item for sublist in E0 for item in sublist], key=lambda k: k[db.DATE])

    print "Stats for entire data set: "
    season_stats(matches)

    tmp = [v for (k, v) in matches.iteritems() if k[0] == 'E0']
    tmp = []
    tmp = [x[db.HOME_TEAM] for x in l2]
    teams = []
    teams = sorted(list(set(tmp)))
    versusTable = map(lambda x: versus_team(l2, x), teams)

    elo_calculate(l2)

#    print_matches(l2)

    pprint(seasonStatsDict)

    for match in l2:
        # Find all matches for home & away teams. This will filter the list down a lot for quicker handling
        hteam_matches = list_matches_before(
            [m for m in l2 if m[db.HOME_TEAM] == match[db.HOME_TEAM] or m[db.HOME_TEAM] == match[db.AWAY_TEAM]],
            match[db.DATE])
        ateam_matches = list_matches_before(
            [m for m in l2 if m[db.AWAY_TEAM] == match[db.HOME_TEAM] or m[db.AWAY_TEAM] == match[db.AWAY_TEAM]],
            match[db.DATE])

        hteam_home = team_matches_home(hteam_matches, match[db.HOME_TEAM])
        hteam_away = team_matches_away(hteam_matches, match[db.HOME_TEAM])
        ateam_home = team_matches_home(ateam_matches, match[db.AWAY_TEAM])
        ateam_away = team_matches_away(ateam_matches, match[db.AWAY_TEAM])
        last_x = lambda x, y: x[-(y+1):-1]
        sum_x = lambda x, y, z: int(field_sum(last_x(x, y), z))
        count_x = lambda x, y, z, w: int(field_count(last_x(x, y), z, w))
        date_sort = lambda x: sorted(x, key=lambda k: k[db.DATE])
        for f in FORM_TABLE:
            # Home team #
            # Home matches only
            match[db.HW + str(f)] = count_x(hteam_home, f, db.FTR, 'H')
            match[db.HD + str(f)] = count_x(hteam_home, f, db.FTR, 'D')
            match[db.FTHGS + str(f)] = sum_x(hteam_home, f, db.FTHG)
            match[db.FTHGC + str(f)] = sum_x(hteam_home, f, db.FTAG)
            # Home and away matches
            match[db.THW + str(f)] = len([m for m in last_x(date_sort(hteam_home + hteam_away), f)
                if ((m[db.HOME_TEAM] == match[db.HOME_TEAM] and m[db.FTR] == 'W') or
                    (m[db.AWAY_TEAM] == match[db.HOME_TEAM] and m[db.FTR] == 'A'))])
            match[db.THD + str(f)] = field_count(
                last_x(date_sort(hteam_home + hteam_away), f), db.FTR, 'D')

            # Away team #
            # Away matches only
            match[db.AW + str(f)] = count_x(ateam_away, f, db.FTR, 'A')
            match[db.AD + str(f)] = count_x(ateam_home, f, db.FTR, 'D')
            match[db.FTAGS + str(f)] = sum_x(ateam_home, f, db.FTAG)
            match[db.FTAGC + str(f)] = sum_x(ateam_home, f, db.FTHG)
            # Home and away matches
            match[db.THW + str(f)] = len([m for m in last_x(date_sort(hteam_home + hteam_away), f)
                                          if ((m[db.HOME_TEAM] == match[db.HOME_TEAM] and m[db.FTR] == 'W') or
                                              (m[db.AWAY_TEAM] == match[db.HOME_TEAM] and m[db.FTR] == 'A'))])
            match[db.TAW + str(f)] = match[db.AW + str(f)] + field_count(last_x(ateam_away, f), db.FTR, 'W')
            match[db.TAD + str(f)] = field_count(
                last_x(date_sort(ateam_home + ateam_away), f), db.FTR, 'D')

    pprint(list_nmatches_before(l2, '14/04/15', 20))

    with open('test.csv', 'wt') as out:
        pprint([m for m in l2 if m[db.HOME_TEAM] == 'Everton'], stream=out)

