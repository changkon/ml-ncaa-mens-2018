import pandas as pd

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

submission = pd.read_csv("input/SampleSubmissionStage1.csv")
playoff_results = pd.read_csv("input/NCAATourneyDetailedResults.csv")
seasons_results = pd.read_csv("input/RegularSeasonDetailedResults.csv")


# https://www.basketball-reference.com/about/glossary.html
def get_pos(row):
    w_half = row.WFGA + 0.4*row.WFTA - 1.07*(row.WOR / (row.WOR + row.LOR))*(row.WFGA - row.WFGM) + row.WTO
    l_half = row.LFGA + 0.4*row.LFTA - 1.07*(row.LOR / (row.LOR + row.WOR))*(row.LFGA - row.LFGM) + row.LTO
    return 0.5*(w_half+l_half)

seasons_results['Pos'] = seasons_results.apply(lambda row: get_pos(row), axis=1)

seasons_results_cpy = seasons_results.copy()
seasons_results_cpy[['WTeamID', 'WScore', 'LTeamID', 'LScore']] = seasons_results_cpy[['LTeamID', 'LScore', 'WTeamID', 'WScore']]

seasons_results = pd.concat([seasons_results, seasons_results_cpy], ignore_index=True)

adv_stat_team_season = seasons_results.groupby(['Season', 'WTeamID'])['Pos', 'WScore', 'LScore'].sum()
# pos_team_season = season_games.groupby(['Season', 'WTeamID']).size().reset_index(name='count')
adv_stat_team_season['ORating'] = adv_stat_team_season.apply(lambda row: 100*row.WScore/row.Pos, axis=1)
adv_stat_team_season['DRating'] = adv_stat_team_season.apply(lambda row: 100*row.LScore/row.Pos, axis=1)
adv_stat_team_season = adv_stat_team_season.reset_index()

adv_stat_team_season.drop('Pos', axis=1, inplace=True)
print(adv_stat_team_season.head())
