import pandas as pd

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

    return adv_stat_team_season

print(get_adv_season_stats().head())
