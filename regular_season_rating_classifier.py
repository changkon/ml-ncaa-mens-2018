import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV
import numpy as np
from advanced_stats_starter import get_adv_season_stats
from submission_simulation import simulate_submit

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

season_with_adv_stats = pd.read_csv("seasons_results_adv_stats.csv")
submission = pd.read_csv("input/SampleSubmissionStage1.csv")
adv_stat_team_season = get_adv_season_stats()

# discard first half of the season
season_with_adv_stats = season_with_adv_stats[season_with_adv_stats['DayNum'] >= 66]

season_with_adv_stats = season_with_adv_stats.drop(['Season', 'DayNum', 'WTeamID', 'LTeamID'], axis=1)

# dropping any rows that have a 0 value
season_with_adv_stats = season_with_adv_stats[(season_with_adv_stats != 0).all(1)]

print(season_with_adv_stats.head())

season_with_adv_stats['Result'] = 1

season_with_adv_stats_copy = season_with_adv_stats.copy()

train_w_stat = ['WDRating', 'WFourFactors', 'WNRating', 'WORating']
train_l_stat = ['LDRating', 'LFourFactors', 'LNRating', 'LORating']

season_with_adv_stats_copy[train_w_stat + train_l_stat] = season_with_adv_stats_copy[train_l_stat + train_w_stat]
season_with_adv_stats_copy['Result'] = 0

season_with_adv_stats = pd.concat([season_with_adv_stats, season_with_adv_stats_copy], ignore_index=True)

y_train = season_with_adv_stats['Result'].values
X_train = season_with_adv_stats.drop('Result', axis=1)

# this is just to try using NRating only as input
# X_train = X_train.drop(['WDRating', 'LDRating', 'WORating', 'LORating', 'LFourFactors', 'WFourFactors'], axis=1)
# print(X_train.head())

logreg = LogisticRegression()
params = {'C': np.logspace(start=-5, stop=3, num=9)}
clf = GridSearchCV(logreg, params, scoring='neg_log_loss', refit=True)
clf.fit(X_train, y_train)
print('Best log_loss: {:.4}, with best C: {}'.format(clf.best_score_, clf.best_params_['C']))

prediction = pd.DataFrame()
prediction['Season'] = submission['ID'].str[:4].astype(int)
prediction['WTeamID'] = submission['ID'].str[5:9].astype(int)
prediction['LTeamID'] = submission['ID'].str[10:].astype(int)


train_stats = ['Season', 'TeamID', 'ORating', 'DRating', 'NRating', 'FourFactors']
win_adv_stats = adv_stat_team_season[train_stats].rename(columns={
    'TeamID': 'WTeamID',
    'NRating': 'WNRating',
    'FourFactors': 'WFourFactors',
    'ORating': 'WORating',
    'DRating': 'WDRating'
})

lose_adv_stats = adv_stat_team_season[train_stats].rename(columns={
    'TeamID': 'LTeamID',
    'NRating': 'LNRating',
    'FourFactors': 'LFourFactors',
    'ORating': 'LORating',
    'DRating': 'LDRating'
})

prediction = prediction.merge(lose_adv_stats, on=['Season', 'LTeamID'])
prediction = prediction.merge(win_adv_stats, on=['Season', 'WTeamID'])

reorder_col = ['WDRating', 'WFourFactors', 'WNRating', 'WORating', 'LDRating', 'LFourFactors', 'LNRating', 'LORating']
# reorder_col = ['WNRating', 'LNRating']
prediction = prediction.drop(['Season', 'WTeamID', 'LTeamID'], axis=1)

# prediction = prediction.drop(['WDRating', 'LDRating', 'WORating', 'LORating', 'LFourFactors', 'WFourFactors'], axis=1)

prediction = prediction[reorder_col]

print(prediction.head())
submission['Pred'] = clf.predict_proba(prediction)
simulate_submit(submission)
