__author__ = 'mep'

import csv
from pprint import pprint
from datetime import datetime
from os import listdir
from os.path import isfile, join
import re
from elo import elo_calculate, elo_plot
import db
from decimal import *
#import itertools as IT
#import collections
from itertools import imap, groupby
import plot

FIELDS = [db.DATE, db.HOME_TEAM, db.AWAY_TEAM, db.FTR, db.FTHG, db.FTAG, db.HS, db.HST, db.AS, db.AST, db.HHW, db.HC,
          db.AC, db.HF, db.AF, db.HY, db.AY, db.HR, db.AR, db.ATTENDANCE]
DATE_FORMAT = '%y/%m/%d'

# Dictionaries holding the generated data
matches = {}
season_stats_dict = {}
league_stats_dict = {}
country_stats_dict = {}
team_stats_dict = {}
team_season_stats_dict = {}

# Extract some keys from a dict (the whole match dict is very big, this helps debugging)
extract_dict = lambda keys, dict: reduce(lambda x, y: x.update({y[0]: y[1]}) or x,
                                        map(None, keys, map(dict.get, keys)), {})

flatten_dict = lambda d: [item for sublist in d.itervalues() for item in sublist]
filter_rows = lambda li, field, value: [line for line in li if line[field] == value]
field_sum = lambda li, field: sum(float(line[field]) for line in li)
field_count = lambda li, field, value: len([line for line in li if line[field] == value])
field_avg = lambda li, field: field_sum(li, field) / len(li)
percent = lambda value, count: round2((float(value) / count) * 100)
round2 = lambda value: round(Decimal(float(value)), 2)

def matches_home(li, team):
    for match in li:
        if match[db.HOME_TEAM] == team:
            yield match

#matches_home = lambda li, team: [m for m in li if m[db.HOME_TEAM] == team]
#matches_away = lambda li, team: [m for m in li if m[db.AWAY_TEAM] == team]
def matches_away(li, team):
    for match in li:
        if match[db.AWAY_TEAM] == team:
            yield match

matches_all = lambda li, team: [x for x in matches_home(li, team)] + [x for x in matches_away(li, team)]


nmatches_before = \
    lambda li, date, c: [m for m in li
                               if datetime.strptime(m[db.DATE], DATE_FORMAT) < datetime.strptime(date, DATE_FORMAT)][-c:]


#def matches_before(li, date):
#    for match in li:
#        if datetime.strptime(match[db.DATE], DATE_FORMAT) < datetime.strptime(date, DATE_FORMAT):
#            yield
#        else:
#            raise StopIteration

matches_before = \
    lambda li, date: [m for m in li
                         if datetime.strptime(m[db.DATE], DATE_FORMAT) < datetime.strptime(date, DATE_FORMAT)]
matches_after = \
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


def extract_name_date(filename):
    match = re.match(r'(.+)(\d{4})\-(\d{4})(.*)', filename)
    return (match.group(1), match.group(2)), filename

def open_files(files):
    """
      Open csv files (and .csv$ only)
    """

    if files == '':
        csv_files = [f for f in listdir("csv") if isfile(join("csv", f)) and f.endswith(".csv")]
    else:
        csv_files = files

    print "Using files: " + str(csv_files)

    match_files = dict(imap(extract_name_date, csv_files))

    for ((key1, key2), name) in match_files.iteritems():
        f = open('csv/' + name)
        matches[(key1, key2)] = []
        reader = csv.DictReader(f)
        for line in reader:
            # Make the dict a bit shorter, at least for now. This will be removed later.
            shortDict = extract_dict(FIELDS, line)
            if shortDict[db.DATE] == '':
                continue
            try:
                shortDict[db.DATE] = datetime.strptime(shortDict[db.DATE], '%d/%m/%y').strftime(DATE_FORMAT)
            except:
                shortDict[db.DATE] = datetime.strptime(shortDict[db.DATE], '%d/%m/%Y').strftime(DATE_FORMAT)

            matches[(key1, key2)].append(shortDict)
        f.close()


def calc_result_related(matches, result):
    result['HWIN'] = percent(field_count(matches, db.FTR, "H"), len(matches))
    result['AWIN'] = percent(field_count(matches, db.FTR, "A"), len(matches))
    result['DRAW'] = percent(field_count(matches, db.FTR, "D"), len(matches))


def calc_goal_related(matches, result):
    result['HGOALS'] = round2(field_avg(matches, db.FTHG))
    result['AGOALS'] = round2(field_avg(matches, db.FTAG))
    result['NOHGOALS'] = percent(field_count(matches, db.FTHG, '0'), len(matches))
    result['NOAGOALS'] = percent(field_count(matches, db.FTAG, '0'), len(matches))
    result['NUM_MATCHES'] = len(matches)


def season_stats(l):
    for (key, season) in l.iteritems():
        d = {}
        calc_result_related(season, d)
        calc_goal_related(season, d)
        season_stats_dict[key] = d


def league_stats(l):
    pass


def team_stats(l):
    for k, g in groupby(sorted(flatten_dict(l), key=lambda k: k[db.HOME_TEAM]), lambda x: x[db.HOME_TEAM]):
        if not (k, 'home') in team_stats_dict:
            team_stats_dict[(k, 'home')] = {}
        tlist = [x for x in g]
        calc_result_related(tlist, team_stats_dict[(k, 'home')])
        calc_goal_related(tlist, team_stats_dict[(k, 'home')])
    for k, g in groupby(sorted(flatten_dict(l), key=lambda k: k[db.AWAY_TEAM]), lambda x: x[db.AWAY_TEAM]):
        if not (k, 'away') in team_stats_dict:
            team_stats_dict[(k, 'away')] = {}
        tlist = [x for x in g]
        calc_result_related(tlist, team_stats_dict[(k, 'away')])
        calc_goal_related(tlist, team_stats_dict[(k, 'away')])


def homematch_stats(m, record):
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


def awaymatch_stats(m, record):
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
    homelist = [v for v in l if v[db.HOME_TEAM] == team]
    awaylist = [v for v in l if v[db.AWAY_TEAM] == team]

    for match in homelist:
        awayteam = match[db.AWAY_TEAM]
        if (awayteam, "home") not in retval:
            retval[(awayteam, "home")] = {"Wins": 0, "Draws": 0, "Losses": 0, db.FTHG: 0, db.FTAG: 0}
        retval[(awayteam, "home")] = homematch_stats(match, retval[(awayteam, "home")])
    for match in awaylist:
        hometeam = match[db.HOME_TEAM]
        if (hometeam, "away") not in retval:
            retval[(hometeam, "away")] = {"Wins": 0, "Draws": 0, "Losses": 0, db.FTHG: 0, db.FTAG: 0}
        retval[(hometeam, "away")] = awaymatch_stats(match, retval[(hometeam, "away")])
    return {team: retval}


if __name__ == '__main__':
    #open_files("")
    open_files(["E02013-2014.csv"])

    l = flatten_dict(matches)

    # Get list items in a flat list
    E0 = [v for (k, v) in matches.iteritems() if k[0] == 'E0']
    matches_bydate = sorted([item for sublist in E0 for item in sublist], key=lambda k: k[db.DATE])

    print "Stats for entire data set: "
    season_stats(matches)

    tmp = [v for (k, v) in matches.iteritems() if k[0] == 'E0']
    tmp = []
    tmp = [x[db.HOME_TEAM] for x in matches_bydate]
    teams = []
    teams = sorted(list(set(tmp)))
    versustable = map(lambda x: versus_team(matches_bydate, x), teams)

    team_stats(matches)

    elo_calculate(matches_bydate)

#    print_matches(l2)

    pprint(season_stats_dict)

    for match in matches_bydate:
        # Find all matches for home & away teams. This will filter the list down a lot for quicker handling
        hteam_matches = matches_before(
            [m for m in matches_bydate if m[db.HOME_TEAM] == match[db.HOME_TEAM] or m[db.HOME_TEAM] == match[db.AWAY_TEAM]],
            match[db.DATE])
        ateam_matches = matches_before(
            [m for m in matches_bydate if m[db.AWAY_TEAM] == match[db.HOME_TEAM] or m[db.AWAY_TEAM] == match[db.AWAY_TEAM]],
            match[db.DATE])

        match[db.MONTH] = int(datetime.strptime(match[db.DATE], DATE_FORMAT).strftime("%m"))
        match[db.WEEKDAY] = int(datetime.strptime(match[db.DATE], DATE_FORMAT).strftime("%w"))
        hteam_home = [x for x in matches_home(hteam_matches, match[db.HOME_TEAM])]
        hteam_away = [x for x in matches_away(hteam_matches, match[db.HOME_TEAM])]
        ateam_home = [x for x in matches_home(ateam_matches, match[db.AWAY_TEAM])]
        ateam_away = [x for x in matches_away(ateam_matches, match[db.AWAY_TEAM])]
        last_x = lambda x, y: x[-(y+1):-1]
        sum_x = lambda x, y, z: field_sum(last_x(x, y), z)
        avg_x = lambda x,y: x / float(y)
        count_x = lambda x, y, z, w: int(field_count(last_x(x, y), z, w))
        date_sort = lambda x: sorted(x, key=lambda k: k[db.DATE])
        for f in db.FORM_TABLE:
            # Home team #
            # Home matches only
            match[db.HW + str(f)] = count_x(hteam_home, f, db.FTR, 'H')
            match[db.HD + str(f)] = count_x(hteam_home, f, db.FTR, 'D')
            match[db.FTHGS + str(f)] = avg_x(sum_x(hteam_home, f, db.FTHG), f)
            match[db.FTHGC + str(f)] = avg_x(sum_x(hteam_home, f, db.FTAG), f)
            match[db.HS + str(f)] = avg_x(sum_x(hteam_home, f, db.HS), f)
            match[db.HST + str(f)] = avg_x(sum_x(hteam_home, f, db.HST), f)
            match[db.HC + str(f)] = avg_x(sum_x(hteam_home, f, db.HC), f)
            match[db.HCC + str(f)] = avg_x(sum_x(hteam_home, f, db.AC), f)
            match[db.HF + str(f)] = avg_x(sum_x(hteam_home, f, db.HF), f)
            match[db.HFA + str(f)] = avg_x(sum_x(hteam_home, f, db.AF), f)
            match[db.HY + str(f)] = avg_x(sum_x(hteam_home, f, db.HY), f)
            match[db.HYA + str(f)] = avg_x(sum_x(hteam_home, f, db.AY), f)
#            match[db.HTHA + str(f)] = avg_x(sum_x(hteam_home, f, db.ATTENDANCE), f)
#            match[db.HTAA + str(f)] = avg_x(sum_x(hteam_away, f, db.ATTENDANCE), f)
            # Home and away matches
            match[db.THW + str(f)] = len([m for m in last_x(date_sort(hteam_home + hteam_away), f)
                if ((m[db.HOME_TEAM] == match[db.HOME_TEAM] and m[db.FTR] == 'W') or
                    (m[db.AWAY_TEAM] == match[db.HOME_TEAM] and m[db.FTR] == 'A'))])
            match[db.THD + str(f)] = field_count(
                last_x(date_sort(hteam_home + hteam_away), f), db.FTR, 'D')

            # Away team #
            # Away matches only
            match[db.AW + str(f)] = count_x(ateam_away, f, db.FTR, 'A')
            match[db.AD + str(f)] = count_x(ateam_away, f, db.FTR, 'D')
            match[db.FTAGS + str(f)] = avg_x(sum_x(ateam_away, f, db.FTAG), f)
            match[db.FTAGC + str(f)] = avg_x(sum_x(ateam_away, f, db.FTHG),f )
            match[db.AS + str(f)] = avg_x(sum_x(ateam_home, f, db.AS), f)
            match[db.AST + str(f)] = avg_x(sum_x(ateam_home, f, db.AST), f)
            match[db.AC + str(f)] = avg_x(sum_x(ateam_home, f, db.AC), f)
            match[db.ACC + str(f)] = avg_x(sum_x(ateam_home, f, db.HC), f)
            match[db.AF + str(f)] = avg_x(sum_x(ateam_home, f, db.AF), f)
            match[db.AFA + str(f)] = avg_x(sum_x(ateam_home, f, db.HF), f)
            match[db.AY + str(f)] = avg_x(sum_x(ateam_home, f, db.AY), f)
            match[db.AYA + str(f)] = avg_x(sum_x(ateam_home, f, db.HY), f)
#            match[db.ATHA + str(f)] = avg_x(sum_x(ateam_home, f, db.ATTENDANCE), f)
#            match[db.ATAA + str(f)] = avg_x(sum_x(ateam_away, f, db.ATTENDANCE), f)
            # Home and away matches
            match[db.THW + str(f)] = len([m for m in last_x(date_sort(hteam_home + hteam_away), f)
                                          if ((m[db.HOME_TEAM] == match[db.HOME_TEAM] and m[db.FTR] == 'W') or
                                              (m[db.AWAY_TEAM] == match[db.HOME_TEAM] and m[db.FTR] == 'A'))])
            match[db.TAW + str(f)] = match[db.AW + str(f)] + field_count(last_x(ateam_away, f), db.FTR, 'W')
            match[db.TAD + str(f)] = field_count(
                last_x(date_sort(ateam_home + ateam_away), f), db.FTR, 'D')

#    pprint(nmatches_before(matches_bydate, '14/04/15', 20))

    e = sorted([x for x in matches_all(matches_bydate, 'Everton')], key=lambda k: k[db.DATE])
#    pprint(e)
#    with open('test.csv', 'wt') as out:
#        pprint([m for m in matches_bydate if m[db.HOME_TEAM] == 'Everton'], stream=out)

    db.matches_to_db(e, 'test.csv', 'text')
    #pprint([extract_dict(db.DB_FIELDS, row) for row in e])
    db.matches_to_db(e, 'test.txt', 'text', do_filtering=True)
    db.season_to_db(season_stats_dict, 'test2.txt', output_type='text')
    db.season_to_db(season_stats_dict, 'test2.csv', output_type='csv')

    elo_plot(matches_bydate)
#    pprint(team_stats_dict)
#    db.to_db([extract_dict(db.DB_FIELDS, row) for row in e], 'test.txt', 'text')
    #db.to_db([extract_dict(db.DB_FIELDS, row) for row in e], 'test.txt', 'text')

