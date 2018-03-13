import pandas as pd
import numpy as np

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

# https://www.basketball-reference.com/about/glossary.html
def get_pos(row):
    w_half = row.WFGA + 0.4*row.WFTA - 1.07*(row.WOR / (row.WOR + row.LDR))*(row.WFGA - row.WFGM) + row.WTO
    l_half = row.LFGA + 0.4*row.LFTA - 1.07*(row.LOR / (row.LOR + row.WDR))*(row.LFGA - row.LFGM) + row.LTO
    return 0.5*(w_half+l_half)

def get_four_factor(row):
    # Shooting the ball
    efg = (row.WFGM + 0.5 * row.WFGM3) / row.WFGA

    # Taking care of the ball
    turnover_rate = row.WTO / (row.WFGA + 0.44 * row.WFTA + row.WTO)

    # Offensive rebounding
    offensive_rebounding_percentage = row.WOR / (row.WOR + row.LDR)

    # Free throw rate
    free_throw_rate = row.WFTM / row.WFGA

    return 0.4 * efg + 0.25 + turnover_rate + 0.2 * offensive_rebounding_percentage + 0.15 * free_throw_rate


def get_adv_season_stats():
    seasons_results = pd.read_csv("input/RegularSeasonDetailedResults.csv")
    seasons_results.drop(['NumOT', 'DayNum'], axis=1, inplace=True)

    win_stats = ['WTeamID', 'WScore', 'WFGM', 'WFGA', 'WFGM3', 'WFGA3', 'WFTM', 'WFTA', 'WOR', 'WDR', 'WAst', 'WTO', 'WStl', 'WBlk', 'WPF']
    lose_stats = ['LTeamID', 'LScore', 'LFGM', 'LFGA', 'LFGM3', 'LFGA3', 'LFTM', 'LFTA', 'LOR', 'LDR', 'LAst', 'LTO', 'LStl', 'LBlk', 'LPF']

    seasons_results_copy = seasons_results.copy()
    seasons_results_copy[win_stats + lose_stats] = seasons_results_copy[lose_stats + win_stats]

    seasons_results = pd.concat([seasons_results, seasons_results_copy], ignore_index=True)

    adv_stat_team_season = seasons_results.groupby(['Season', 'WTeamID']).sum().reset_index()
    adv_stat_team_season['Pos'] = adv_stat_team_season.apply(get_pos, axis=1)
    adv_stat_team_season['ORating'] = adv_stat_team_season.apply(lambda row: 100*row.WScore/row.Pos, axis=1)
    adv_stat_team_season['DRating'] = adv_stat_team_season.apply(lambda row: 100*row.LScore/row.Pos, axis=1)
    adv_stat_team_season['NRating'] = adv_stat_team_season['ORating'] - adv_stat_team_season['DRating']
    adv_stat_team_season['FourFactors'] = adv_stat_team_season.apply(get_four_factor, axis=1)
    adv_stat_team_season = adv_stat_team_season.drop(['LTeamID'], axis=1)
    adv_stat_team_season = adv_stat_team_season.rename(columns={'WTeamID': 'TeamID'})

    print(adv_stat_team_season.head())

    return adv_stat_team_season


def get_adv_stats_per_season_game():
    seasons_results = pd.read_csv("input/RegularSeasonDetailedResults.csv")
    seasons_results = seasons_results.sort_values(['Season', 'DayNum'])

    team_stats = {}
    rating_per_game = pd.DataFrame()
    print(seasons_results.shape)
    print(rating_per_game.dtypes)
    for index, row in seasons_results.iterrows():
        # find rating for WTeamID first
        # print(index)
        isCurrentSeason = seasons_results['Season'] == row.Season

        isPrevGames = seasons_results['DayNum'] < row.DayNum
        w_orating = 0.0
        w_drating = 0.0
        w_nrating = 0.0
        w_four_factors = 0.0
        l_orating = 0.0
        l_drating = 0.0
        l_nrating = 0.0
        l_four_factors = 0.0

        past_games = seasons_results[isCurrentSeason & isPrevGames]
        if past_games.empty:
            continue

        past_games_copy = past_games.copy()
        win_stats = ['WTeamID', 'WScore', 'WFGM', 'WFGA', 'WFGM3', 'WFGA3', 'WFTM', 'WFTA', 'WOR', 'WDR', 'WAst',
                     'WTO', 'WStl', 'WBlk', 'WPF']
        lose_stats = ['LTeamID', 'LScore', 'LFGM', 'LFGA', 'LFGM3', 'LFGA3', 'LFTM', 'LFTA', 'LOR', 'LDR', 'LAst',
                      'LTO', 'LStl', 'LBlk', 'LPF']

        past_games_copy[win_stats + lose_stats] = past_games_copy[lose_stats + win_stats]
        past_games = pd.concat([past_games, past_games_copy], ignore_index=True)

        past_games_groupby = past_games.groupby('WTeamID').sum().reset_index()
        past_games_groupby['Pos'] = past_games_groupby.apply(get_pos, axis=1)
        past_games_groupby['ORating'] = past_games_groupby.apply(lambda row: 100 * row.WScore / row.Pos, axis=1)
        past_games_groupby['DRating'] = past_games_groupby.apply(lambda row: 100 * row.LScore / row.Pos, axis=1)
        past_games_groupby['NRating'] = past_games_groupby['ORating'] - past_games_groupby['DRating']
        past_games_groupby['FourFactors'] = past_games_groupby.apply(get_four_factor, axis=1)
        past_games_groupby = past_games_groupby.drop(['LTeamID'], axis=1)
        past_games_groupby = past_games_groupby.rename(columns={'WTeamID': 'TeamID'})

        # helper function to retrieve the values
        def get_adv_stats_for_team(team_row):
            orating = team_row['ORating']
            drating = team_row['DRating']
            nrating = team_row['NRating']
            four_factors = team_row['FourFactors']

            # for some reason, sometime these value are actually Serie object !!! so have to do this
            if not isinstance(orating, float):
                orating = team_row['ORating'].values[0]
                drating = team_row['DRating'].values[0]
                nrating = team_row['NRating'].values[0]
                four_factors = team_row['FourFactors'].values[0]

            return orating, drating, nrating, four_factors

        wteam_row = past_games_groupby[past_games_groupby['TeamID'] == row.WTeamID]
        if not wteam_row.empty:
            w_orating, w_drating, w_nrating, w_four_factors = get_adv_stats_for_team(wteam_row)

        lteam_row = past_games_groupby[past_games_groupby['TeamID'] == row.LTeamID]
        if not lteam_row.empty:
            l_orating, l_drating, l_nrating, l_four_factors = get_adv_stats_for_team(lteam_row)

        new_row = {
            'Season': row.Season,
            'DayNum': row.DayNum,
            'WTeamID': row.WTeamID,
            'LTeamID': row.LTeamID,
            'WORating': w_orating,
            'WDRating': w_drating,
            'WNRating': w_nrating,
            'WFourFactors': w_four_factors,
            'LORating': l_orating,
            'LDRating': l_drating,
            'LNRating': l_nrating,
            'LFourFactors': l_four_factors,

        }
        rating_per_game = rating_per_game.append(new_row, ignore_index=True)

    # need to merge the rating back into the season game
    seasons_results = seasons_results.merge(rating_per_game, on=['Season', 'DayNum', 'WTeamID', 'LTeamID'])

    output_columns = ['Season', 'DayNum', 'WTeamID', 'LTeamID', 'LDRating',  'LFourFactors', 'LNRating', 'LORating',
                      'WDRating', 'WFourFactors', 'WNRating', 'WORating']
    seasons_results = seasons_results[output_columns]
    print(seasons_results.tail())
    return seasons_results
    # seasons_results.to_csv('seasons_results_adv_stats.csv', index=False)

def get_regular_season_temp():
    seasons_results = pd.read_csv("input/RegularSeasonDetailedResults.csv")
    seasons_results = seasons_results.sort_values(['Season', 'DayNum'])

    # Keep a dict to store current team accumulated stats
    team_stats = {}
    advanced_stats_per_game = pd.DataFrame()

    initial_stats = {
        'score': 0,
        'fgm': 0,
        'fga': 0,
        'fgm3': 0,
        'fga3': 0,
        'ftm': 0,
        'fta': 0,
        'or': 0,
        'dr': 0,
        'ast': 0,
        'to': 0,
        'stl': 0,
        'blk': 0,
        'pf': 0,
        'oscore': 0,
        'ofgm': 0,
        'ofga': 0,
        'ofgm3': 0,
        'ofga3': 0,
        'oftm': 0,
        'ofta': 0,
        'oor': 0,
        'odr': 0,
        'oast': 0,
        'oto': 0,
        'ostl': 0,
        'oblk': 0,
        'opf': 0,
        'gp': 0
    }

    def get_pos(wfga, wfta, wor, wfgm, wto, wdr, lfga, lfta, lor, lfgm, lto, ldr):
        w_half = wfga + 0.4 * wfta - 1.07 * (wor / (wor + ldr)) * (wfga - wfgm) + wto
        l_half = lfga + 0.4 * lfta - 1.07 * (lor / (lor + wdr)) * (lfga - lfgm) + lto
        return 0.5 * (w_half + l_half)

    def get_four_factor(fgm, fgm3, fga, to, fta, oR, oDr, ftm):
        # Shooting the ball
        efg = (fgm + 0.5 * fgm3) / fga

        # Taking care of the ball
        turnover_rate = to / (fga + 0.44 * fta + to)

        # Offensive rebounding
        offensive_rebounding_percentage = oR / (oR + oDr)

        # Free throw rate
        free_throw_rate = ftm / fga

        return 0.4 * efg + 0.25 + turnover_rate + 0.2 * offensive_rebounding_percentage + 0.15 * free_throw_rate

    for index, row in seasons_results.iterrows():
        wteam_current_stats = team_stats.get((row.Season, row.WTeamID), initial_stats)
        lteam_current_stats = team_stats.get((row.Season, row.LTeamID), initial_stats)

        # update stats
        team_stats[(row.Season, row.WTeamID)] = {
            'score': wteam_current_stats['score'] + row['WScore'],
            'fgm': wteam_current_stats['fgm'] + row['WFGM'],
            'fga': wteam_current_stats['fga'] + row['WFGA'],
            'fgm3': wteam_current_stats['fgm3'] + row['WFGM3'],
            'fga3': wteam_current_stats['fga3'] + row['WFGA3'],
            'ftm': wteam_current_stats['ftm'] + row['WFTM'],
            'fta': wteam_current_stats['fta'] + row['WFTA'],
            'or': wteam_current_stats['or'] + row['WOR'],
            'dr': wteam_current_stats['dr'] + row['WDR'],
            'ast': wteam_current_stats['ast'] + row['WAst'],
            'to': wteam_current_stats['to'] + row['WTO'],
            'stl': wteam_current_stats['stl'] + row['WStl'],
            'blk': wteam_current_stats['blk'] + row['WBlk'],
            'pf': wteam_current_stats['pf'] + row['WPF'],
            # Update opponent
            'oscore': wteam_current_stats['oscore'] + row['LScore'],
            'ofgm': wteam_current_stats['ofgm'] + row['LFGM'],
            'ofga': wteam_current_stats['ofga'] + row['LFGA'],
            'ofgm3': wteam_current_stats['ofgm3'] + row['LFGM3'],
            'ofga3': wteam_current_stats['ofga3'] + row['LFGA3'],
            'oftm': wteam_current_stats['oftm'] + row['LFTM'],
            'ofta': wteam_current_stats['ofta'] + row['LFTA'],
            'oor': wteam_current_stats['oor'] + row['LOR'],
            'odr': wteam_current_stats['odr'] + row['LDR'],
            'oast': wteam_current_stats['oast'] + row['LAst'],
            'oto': wteam_current_stats['oto'] + row['LTO'],
            'ostl': wteam_current_stats['ostl'] + row['LStl'],
            'oblk': wteam_current_stats['oblk'] + row['LBlk'],
            'opf': wteam_current_stats['opf'] + row['LPF'],
            'gp': wteam_current_stats['gp'] + 1
        }

        team_stats[(row.Season, row.LTeamID)] = {
            'score': lteam_current_stats['score'] + row['LScore'],
            'fgm': lteam_current_stats['fgm'] + row['LFGM'],
            'fga': lteam_current_stats['fga'] + row['LFGA'],
            'fgm3': lteam_current_stats['fgm3'] + row['LFGM3'],
            'fga3': lteam_current_stats['fga3'] + row['LFGA3'],
            'ftm': lteam_current_stats['ftm'] + row['LFTM'],
            'fta': lteam_current_stats['fta'] + row['LFTA'],
            'or': lteam_current_stats['or'] + row['LOR'],
            'dr': lteam_current_stats['dr'] + row['LDR'],
            'ast': lteam_current_stats['ast'] + row['LAst'],
            'to': lteam_current_stats['to'] + row['LTO'],
            'stl': lteam_current_stats['stl'] + row['LStl'],
            'blk': lteam_current_stats['blk'] + row['LBlk'],
            'pf': lteam_current_stats['pf'] + row['LPF'],
            # Update opponent
            'oscore': lteam_current_stats['oscore'] + row['WScore'],
            'ofgm': lteam_current_stats['ofgm'] + row['WFGM'],
            'ofga': lteam_current_stats['ofga'] + row['WFGA'],
            'ofgm3': lteam_current_stats['ofgm3'] + row['WFGM3'],
            'ofga3': lteam_current_stats['ofga3'] + row['WFGA3'],
            'oftm': lteam_current_stats['oftm'] + row['WFTM'],
            'ofta': lteam_current_stats['ofta'] + row['WFTA'],
            'oor': lteam_current_stats['oor'] + row['WOR'],
            'odr': lteam_current_stats['odr'] + row['WDR'],
            'oast': lteam_current_stats['oast'] + row['WAst'],
            'oto': lteam_current_stats['oto'] + row['WTO'],
            'ostl': lteam_current_stats['ostl'] + row['WStl'],
            'oblk': lteam_current_stats['oblk'] + row['WBlk'],
            'opf': lteam_current_stats['opf'] + row['WPF'],
            'gp': lteam_current_stats['gp'] + 1
        }

        wteam_updated_current_stats = team_stats.get((row.Season, row.WTeamID), initial_stats)
        lteam_updated_current_stats = team_stats.get((row.Season, row.LTeamID), initial_stats)
        # Do winning stats
        wPos = get_pos(wteam_updated_current_stats['fga'], wteam_updated_current_stats['fta'],
                       wteam_updated_current_stats['or'], wteam_updated_current_stats['fgm'],
                       wteam_updated_current_stats['to'], wteam_updated_current_stats['dr'],
                       wteam_updated_current_stats['ofga'], wteam_updated_current_stats['ofta'],
                       wteam_updated_current_stats['oor'], wteam_updated_current_stats['ofgm'],
                       wteam_updated_current_stats['oto'], wteam_updated_current_stats['odr'])

        lPos = get_pos(lteam_updated_current_stats['fga'], lteam_updated_current_stats['fta'],
                       lteam_updated_current_stats['or'], lteam_updated_current_stats['fgm'],
                       lteam_updated_current_stats['to'], lteam_updated_current_stats['dr'],
                       lteam_updated_current_stats['ofga'], lteam_updated_current_stats['ofta'],
                       lteam_updated_current_stats['oor'], lteam_updated_current_stats['ofgm'],
                       lteam_updated_current_stats['oto'], lteam_updated_current_stats['odr'])

        wORtg = 100 * wteam_updated_current_stats['score'] / wPos
        lORtg = 100 * lteam_updated_current_stats['score'] / lPos

        wDRtg = 100 * wteam_updated_current_stats['oscore'] / wPos
        lDRtg = 100 * lteam_updated_current_stats['oscore'] / lPos

        wNRtg = wORtg - wDRtg
        lNRtg = lORtg - lDRtg

        wFourFactors = get_four_factor(wteam_updated_current_stats['fgm'], wteam_updated_current_stats['fgm3'],
                                       wteam_updated_current_stats['fga'],
                                       wteam_updated_current_stats['to'], wteam_updated_current_stats['fta'],
                                       wteam_updated_current_stats['or'], wteam_updated_current_stats['odr'],
                                       wteam_updated_current_stats['ftm'])

        lFourFactors = get_four_factor(lteam_updated_current_stats['fgm'], lteam_updated_current_stats['fgm3'],
                                       lteam_updated_current_stats['fga'],
                                       lteam_updated_current_stats['to'], lteam_updated_current_stats['fta'],
                                       lteam_updated_current_stats['or'], lteam_updated_current_stats['odr'],
                                       lteam_updated_current_stats['ftm'])

        new_row = {
            'Season': row.Season,
            'DayNum': row.DayNum,
            'WTeamID': row.WTeamID,
            'LTeamID': row.LTeamID,
            'WORating': wORtg,
            'WDRating': wDRtg,
            'WNRating': wNRtg,
            'WFourFactors': wFourFactors,
            'LORating': lORtg,
            'LDRating': lDRtg,
            'LNRating': lNRtg,
            'LFourFactors': lFourFactors
        }

        advanced_stats_per_game.append(new_row, ignore_index=True)

    return advanced_stats_per_game

john_adv = get_adv_stats_per_season_game()
john_adv.to_csv('regular-season-adv.csv', index=False)

alt_adv = get_regular_season_temp()
alt_adv.to_csv('regular-season-alt-adv.csv', index=False)