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
        print(index)
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
    # seasons_results.to_csv('seasons_results_adv_stats.csv', index=False)
