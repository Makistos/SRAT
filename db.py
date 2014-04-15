__author__ = 'mep'

import csv
from prettytable import PrettyTable

DATE = 'Date'           # Date, this is fixed to format yy/mm/dd for easier sorting
HOME_TEAM = 'HomeTeam'
AWAY_TEAM = 'AwayTeam'
REFEREE = 'Referee'     # Referee name
ATTENDANCE = 'ATTENDANCE'
FTR = 'FTR'             # Full-time result
FTHG = 'FTHG'           # Full-time home goals
FTAG = 'FTAG'           # Full-time away goals
HE = 'HE'               # Home ELO rating before match
HEC = 'HEC'             # Home ELO rating change from before
AE = 'AE'               # Away ELO rating before match
AEC = 'AEC'             # Away ELO rating change from before
HS = 'HS'               # Home team shots
AS = 'AS'               # Away team shots
HST = 'HST'             # Home team shots on target
AST = 'AST'             # Away team shots on target
HC = 'HC'               # Home team corners
AC = 'AC'               # Away team corners
HHW = 'HHW'             # Home team hit woodwork
AHW = 'AHW'             # Away team hit woodwork
HF = 'HF'               # Home team fouls commited
AF = 'AF'               # Away team fouls commited
HO = 'HO'               # Home team offsides
AO = 'AO'               # Away team offsides
HY = 'HY'               # Home team yellow cards
AY = 'AY'               # Away team yellow cards
HR = 'HR'               # Home team red cards
AR = 'AR'               # Away team red cards

HW = 'HW'             # Home wins for last x (for home team)
HD = 'HD'             # Home draws for last x (for home team)
THW = 'THW'           # Total wins for home team in last x
THD = 'THD'           # Total draws for home team in last x
AW = 'AW'             # Away wins for last x (for away team)
AD = 'AD'             # Away draws for last x (for away team)
TAW = 'THW'           # Total wins for away team in last x
TAD = 'THD'           # Total draws for away team in last x
FTHGS = 'FTHGS'       # Full-time goals scored for last x home games (home team)
FTHGC = 'FTHGC'       # Full-time goals conceded for last x home games (home team)
FTAGS = 'FTAGS'         # Full-time goals for last x away games (away team)
FTAGC = 'FTAGC'       # Full-time goals conceded for last x away games (away team)
FTTHGS = 'FTTHGS'       # Total number of goals scored by home team in last x
FTTHGC = 'FTTHGC'       # Total number of goals conceded by home team in last x
FTTAGS = 'FTTAGS'       # Total number of goals scored by away team in last x
FTTAGC = 'FTTAGC'       # Total number of goals conceded by away tem in last x

FORM_TABLE = [2, 4, 6, 10, 15]  # Match lengths to which to calculate the form parameters

# Fields that are written to db/txt/csv
ALL_FIELDS = [DATE, HOME_TEAM, AWAY_TEAM, FTR, FTHG, FTAG, HS, HST, AS, AST]
TXT_FIELDS = [DATE, HOME_TEAM, AWAY_TEAM, FTR, FTHG, FTAG, HE, AE]
DB_FIELDS = ALL_FIELDS
CSV_FIELDS = TXT_FIELDS

def map_value(data, field_map):
    for f in field_map:
        yield data[f]

def to_db(data, file_name, output_type='text', do_filtering=False):
    """
    Saves the data in the parameter to "type" where type can be "text", "db" or "csv".
    """

    if not do_filtering:
        fields = list(data[0].keys())
    else:
        fields = TXT_FIELDS

    if output_type == 'text':
        tbl = PrettyTable(fields)
        map(tbl.add_row, [[x for x in map_value(d, fields)] for d in data])
        f = open(file_name, 'w')
        f.write(tbl.get_string())
    elif output_type == 'db':
        pass
    elif output_type == 'csv':
        csvfile = open(file_name, 'wb')
        writer = csv.DictWriter(csvfile, delimiter=',', fieldnames=fields, restval='', extrasaction='ignore', dialect='excel')
        writer.writeheader()
        map(writer.writerow, data)
    else:
        print("Unknown writer type %s." % output_type)
