__author__ = 'mep'


we = lambda old, opp, adj:  (1.0 / (10**(-(old - opp + adj)/400.0) + 1.0))


def elo_adjust(match, home_elo, away_elo):

    home = elo_calc_change(int(home_elo), int(away_elo), True, int(match["FTHG"]), int(match["FTAG"]))
    away = elo_calc_change(int(away_elo), int(home_elo), False, int(match["FTAG"]), int(match["FTHG"]))

    return home, away


def elo_calc_change(old_value, opp_value, is_home, scored, conceded):
    """

    @rtype : float
    @param old_value: Current value that will be fixed
    @param opp_value: Opponent's rating
    @param is_home: Was this a home game?
    @param scored: How many goals team scored
    @param conceded: How many goals team conceded
    @return Change in rating

    This function calculates the change in the rating using the world football
    ELO rating. The formula is:

    R = KG * (W - We)

    Where G is goal difference. If the game was won with one goal or less this is not adjusted.
    For two goal difference it is 3/2 and if it's greater than two, (11+N)/8 where N is goal difference.

    K is 20 which is the same as the coefficient in friendly international matches. Adjusting this will make
    changes bigger or smaller.

    W is the result, win = 1, draw = 0,5, loss = 0.

    We is expected result, calculated with

    We = 1 / (10^(-dr/400)+1)

    Where dr is the difference in rating. 100 is added if this was a home match.
    """

    g_diff = abs(scored - conceded)

    g = 0.0

    if g_diff < 2:
        g = 1.0
    elif g_diff == 2:
        g = 3/2.0
    else:
        g = (11 + g_diff) / 8.0

    home_adj = 0.0
    if is_home:
        home_adj = 100.0

    if (scored > conceded):
        result = 1.0
    elif (scored == conceded):
        result = 0.5
    else:
        result = 0.0

    r = 20.0 * g * (result - we(old_value, opp_value, home_adj))

    return r
