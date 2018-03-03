import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV
import sklearn.metrics as metrics

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

submission = pd.read_csv("input/SampleSubmissionStage1.csv")
# playoff_results = pd.read_csv("input/NCAATourneyDetailedResults.csv")
compact_playoff_results = pd.read_csv("input/NCAATourneyCompactResults.csv")
playoff_seeds = pd.read_csv("input/NCAATourneySeeds.csv")
seasons_results = pd.read_csv("input/RegularSeasonDetailedResults.csv")
seasons_results.drop(['NumOT', 'DayNum'], axis=1, inplace=True)

# https://www.basketball-reference.com/about/glossary.html
def get_pos(row):
    w_half = row.WFGA + 0.4*row.WFTA - 1.07*(row.WOR / (row.WOR + row.LDR))*(row.WFGA - row.WFGM) + row.WTO
    l_half = row.LFGA + 0.4*row.LFTA - 1.07*(row.LOR / (row.LOR + row.WDR))*(row.LFGA - row.LFGM) + row.LTO
    return 0.5*(w_half+l_half)


def seed_to_int(seed):
    #Get just the digits from the seeding. Return as int
    s_int = int(seed[1:3])
    return s_int

win_stats = ['WTeamID', 'WScore', 'WFGM', 'WFGA', 'WFGM3', 'WFGA3', 'WFTM', 'WFTA', 'WOR', 'WDR', 'WAst', 'WTO', 'WStl', 'WBlk', 'WPF']
lose_stats = ['LTeamID', 'LScore', 'LFGM', 'LFGA', 'LFGM3', 'LFGA3', 'LFTM', 'LFTA', 'LOR', 'LDR', 'LAst', 'LTO', 'LStl', 'LBlk', 'LPF']

seasons_results_copy = seasons_results.copy()
seasons_results_copy[win_stats + lose_stats] = seasons_results_copy[lose_stats + win_stats]

seasons_results = pd.concat([seasons_results, seasons_results_copy], ignore_index=True)

adv_stat_team_season = seasons_results.groupby(['Season', 'WTeamID']).sum().reset_index()
adv_stat_team_season['Pos'] = adv_stat_team_season.apply(get_pos, axis=1)
adv_stat_team_season['ORating'] = adv_stat_team_season.apply(lambda row: 100*row.WScore/row.Pos, axis=1)
adv_stat_team_season['DRating'] = adv_stat_team_season.apply(lambda row: 100*row.LScore/row.Pos, axis=1)
adv_stat_team_season = adv_stat_team_season.drop(['LTeamID'], axis=1)
adv_stat_team_season = adv_stat_team_season.rename(columns={'WTeamID': 'TeamID'})

# lets use data from 2003-2013 to train the modal
train = compact_playoff_results.loc[(compact_playoff_results['Season'] >= 2003) & (compact_playoff_results['Season'] <= 2013)]
train = train.drop(['DayNum', 'WScore', 'LScore', 'WLoc', 'NumOT'], axis=1)

train_stats = ['Season', 'TeamID', 'ORating', 'DRating']
win_adv_stats = adv_stat_team_season[train_stats].rename(columns={'TeamID': 'WTeamID', 'ORating': 'WORating', 'DRating': 'WDRating'})
lose_adv_stats = adv_stat_team_season[train_stats].rename(columns={'TeamID': 'LTeamID', 'ORating': 'LORating', 'DRating': 'LDRating'})
train = train.merge(win_adv_stats, on=['Season', 'WTeamID'])
train = train.merge(lose_adv_stats, on=['Season', 'LTeamID'])

playoff_seeds['seed_int'] = playoff_seeds.Seed.apply(seed_to_int)
playoff_seeds['seed_int'] = playoff_seeds['seed_int'].abs()
playoff_seeds.drop('Seed', inplace=True, axis=1)

winseeds = playoff_seeds.rename(columns={'TeamID': 'WTeamID', 'seed_int': 'WSeed'})
lossseeds = playoff_seeds.rename(columns={'TeamID': 'LTeamID', 'seed_int': 'LSeed'})

train = train.merge(winseeds, on=['Season', 'WTeamID'])
train = train.merge(lossseeds, on=['Season', 'LTeamID'])
train['SeedDiff'] = train.WSeed - train.LSeed
train = train.drop(['Season', 'WTeamID', 'LTeamID'], axis=1)
train['Result'] = 1

train_copy = train.copy()

train_w_stat = ['WORating', 'WDRating', 'WSeed']
train_l_stat = ['LORating', 'LDRating', 'LSeed']

train_copy[train_w_stat + train_l_stat] = train_copy[train_l_stat + train_w_stat]
train_copy['Result'] = 0

train = pd.concat([train, train_copy], ignore_index=True)

y_train = train['Result'].values
X_train = train.drop('Result', axis=1)

logreg = LogisticRegression()
params = {'C': np.logspace(start=-5, stop=3, num=9)}
clf = GridSearchCV(logreg, params, scoring='neg_log_loss', refit=True)
clf.fit(X_train, y_train)
print('Best log_loss: {:.4}, with best C: {}'.format(clf.best_score_, clf.best_params_['C']))




# creating test data
prediction = pd.DataFrame()
prediction['Season'] = submission['ID'].str[:4].astype(int)
prediction['WTeamID'] = submission['ID'].str[5:9].astype(int)
prediction['LTeamID'] = submission['ID'].str[10:].astype(int)

# note merging LTeamID first then WTeamID so that the order is WTeamID ascending, same order as the submission
prediction = prediction.merge(lose_adv_stats, on=['Season', 'LTeamID'])
prediction = prediction.merge(win_adv_stats, on=['Season', 'WTeamID'])

prediction = prediction.merge(lossseeds, on=['Season', 'LTeamID'])
prediction = prediction.merge(winseeds, on=['Season', 'WTeamID'])
prediction['SeedDiff'] = prediction.WSeed - prediction.LSeed
prediction = prediction.drop(['Season', 'WTeamID', 'LTeamID'], axis=1)

submission['Pred'] = clf.predict_proba(prediction)

print(submission.head())

# submission.to_csv('logreg_seed_starter.csv', index=False)

# create a local function to meausre the logloss so don't have submit every time
val_start_year = 2014
val_end_year = 2017

val_results = compact_playoff_results.loc[(compact_playoff_results['Season'] >= val_start_year) & (compact_playoff_results['Season'] <= val_end_year)]
val_results = val_results.loc[val_results['DayNum'] >= 136]
val_results = val_results.drop(['DayNum', 'WScore', 'LScore', 'WLoc', 'NumOT'], axis=1)


def create_id(row):
    row_id = str(row.Season) + '_'

    if row.WTeamID < row.LTeamID:
        row_id = row_id + str(row.WTeamID) + '_' + str(row.LTeamID)
    else:
        row_id = row_id + str(row.LTeamID) + '_' + str(row.WTeamID)

    return row_id


def get_result(row):
    if row.WTeamID < row.LTeamID:
        return 1
    else:
        return 0

val_results['ID'] = val_results.apply(create_id, axis=1)
val_results['Result'] = val_results.apply(get_result, axis=1)
val_results = val_results.drop(['WTeamID', 'LTeamID'], axis=1)

final_comparison = submission.merge(val_results, on='ID')

print('final log loss: ', metrics.log_loss(final_comparison['Result'], final_comparison['Pred']))

for target_season in final_comparison.Season.unique():
    temp = final_comparison[ final_comparison['Season'] == target_season]
    print('Season ', target_season, ' log loss: ', metrics.log_loss(temp['Result'], temp['Pred']))