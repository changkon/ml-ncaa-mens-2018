import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV
from advanced_stats_starter import get_adv_season_stats
from submission_simulation import simulate_submit

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

submission = pd.read_csv("input/SampleSubmissionStage1.csv")
compact_playoff_results = pd.read_csv("input/NCAATourneyCompactResults.csv")
playoff_seeds = pd.read_csv("input/NCAATourneySeeds.csv")
seasons_results = pd.read_csv("input/RegularSeasonDetailedResults.csv")
adv_stat_team_season = get_adv_season_stats()

def seed_to_int(seed):
    #Get just the digits from the seeding. Return as int
    s_int = int(seed[1:3])
    return s_int

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
simulate_submit(submission)

# submission.to_csv('logreg_seed_starter.csv', index=False)