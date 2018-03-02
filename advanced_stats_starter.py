import pandas as pd

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

submission = pd.read_csv("input/SampleSubmissionStage1.csv")
playoff_results = pd.read_csv("input/NCAATourneyDetailedResults.csv")
seasons_results = pd.read_csv("input/RegularSeasonDetailedResults.csv")
seasons_results.drop(['NumOT', 'DayNum'], axis=1, inplace=True)


# https://www.basketball-reference.com/about/glossary.html
def get_pos(row):
    w_half = row.WFGA + 0.4*row.WFTA - 1.07*(row.WOR / (row.WOR + row.LDR))*(row.WFGA - row.WFGM) + row.WTO
    l_half = row.LFGA + 0.4*row.LFTA - 1.07*(row.LOR / (row.LOR + row.WDR))*(row.LFGA - row.LFGM) + row.LTO
    return 0.5*(w_half+l_half)

win_stats = ['WTeamID', 'WScore', 'WFGM', 'WFGA', 'WFGM3', 'WFGA3', 'WFTM', 'WFTA', 'WOR', 'WDR', 'WAst', 'WTO', 'WStl', 'WBlk', 'WPF']
lose_stats = ['LTeamID', 'LScore', 'LFGM', 'LFGA', 'LFGM3', 'LFGA3', 'LFTM', 'LFTA', 'LOR', 'LDR', 'LAst', 'LTO', 'LStl', 'LBlk', 'LPF']

seasons_results_copy = seasons_results.copy()
seasons_results_copy[win_stats + lose_stats] = seasons_results_copy[lose_stats + win_stats]

seasons_results = pd.concat([seasons_results, seasons_results_copy], ignore_index=True)

adv_stat_team_season = seasons_results.groupby(['Season', 'WTeamID']).sum()
adv_stat_team_season['Pos'] = adv_stat_team_season.apply(lambda row: get_pos(row), axis=1)
adv_stat_team_season['ORating'] = adv_stat_team_season.apply(lambda row: 100*row.WScore/row.Pos, axis=1)
adv_stat_team_season['DRating'] = adv_stat_team_season.apply(lambda row: 100*row.LScore/row.Pos, axis=1)
print(adv_stat_team_season.head())

