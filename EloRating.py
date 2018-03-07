import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV
#from advanced_stats_starter import get_adv_season_stats
from submission_simulation import simulate_submit

K = 20 #effects how quickly elo adjusts
Home_Advantage = 100
rs = pd.read_csv('input/RegularSeasonCompactResults.csv')
submission = pd.read_csv("input/SampleSubmissionStage1.csv")
rs.drop(["NumOT"], axis=1, inplace=True)
team_ids = set(rs.WTeamID).union(set(rs.LTeamID))
elo_dict = dict(zip(list(team_ids), [1500] * len(team_ids))) #set all team ratings to 1500
rs['margin'] = rs.WScore - rs.LScore # New columns to help us iteratively update elos
rs['w_elo'] = None
rs['l_elo'] = None
#rs['elo_diff'] = None

def elo_pred(elo1, elo2):
	return(1. / (10. ** (-(elo1 - elo2) / 400.) + 1.))

def expected_margin(elo_diff):
	return((7.5 + 0.006 * elo_diff))

def elo_update(w_elo, l_elo, margin):
	elo_diff = w_elo - l_elo
	pred = elo_pred(w_elo, l_elo)
	mult = ((margin + 3.) ** 0.8) / expected_margin(elo_diff)
	update = K * mult * (1 - pred)
	return(pred, update)

assert np.all(rs.index.values == np.array(range(rs.shape[0]))), "Index is out of order."

preds = []

# Loop over all rows of the games dataframe
for i in range(rs.shape[0]):

	# Get key data from current row
	w = rs.at[i, 'WTeamID']
	l = rs.at[i, 'LTeamID']
	margin = rs.at[i, 'margin']
	wloc = rs.at[i, 'WLoc']
	#rs.loc[i, 'elo_diff'] = elo_dict[w] - elo_dict[l] #elo_diff before result of game


	# Does either team get a home-court advantage?
	w_ad, l_ad, = 0., 0.
	if wloc == "H":
		w_ad += Home_Advantage
	elif wloc == "A":
		l_ad += Home_Advantage

	# Get elo updates as a result of the game
	pred, update = elo_update(elo_dict[w] + w_ad,
							  elo_dict[l] + l_ad,
							  margin)
	elo_dict[w] += update
	elo_dict[l] -= update
	preds.append(pred)

	# Stores new elos in the games dataframe
	rs.loc[i, 'w_elo'] = elo_dict[w]
	rs.loc[i, 'l_elo'] = elo_dict[l]

#Using data from 2003-2013 Regular Season
train = rs.loc[(rs['Season'] >= 2003) & (rs['Season'] <= 2013)]
train = train.drop(['DayNum'], axis = 1)
train['elo_diff'] = train.w_elo - train.l_elo
train = train.drop(['Season', 'WTeamID', 'LTeamID'], axis =1)
train['Result'] = 1

train_copy = train.copy()
train_copy[['Season','WScore', 'LScore','WLoc', 'margin', 'w_elo', 'l_elo','elo_diff']] = train_copy[['Season', 'LScore', 'WScore','WLoc', 'margin', 'l_elo', 'w_elo','elo_diff']]
train_copy['Result'] = 0

train = pd.concat([train,train_copy], ignore_index= True)

#Print to show training data used
print(train.head(n=5))

y_train = train['Result'].values
X_train = train.drop('Result', axis = 1)

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
prediction = prediction.merge(rs, on=['Season', 'LTeamID'])
prediction = prediction.merge(rs, on=['Season', 'WTeamID'])
prediction['elo_diff'] = prediction.w_elo - prediction.l_elo
prediction = prediction.drop(['Season', 'WTeamID', 'LTeamID'], axis=1)

submission['Pred'] = clf.predict_proba(prediction)
simulate_submit(submission)
