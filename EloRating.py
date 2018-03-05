import numpy as np
import pandas as pd
from sklearn.metrics import log_loss

K = 20 #effects how quickly elo adjusts
Home_Advantage = 100
rs = pd.read_csv("../input/RegularSeasonCompactResults.csv")
rs.drop(["NumOT"], axis=1, inplace=True)
team_ids = set(rs.WTeamID).union(set(rs.LTeamID))
elo_dict = dict(zip(list(team_ids), [1500] * len(team_ids))) #set all team ratings to 1500
rs['margin'] = rs.WScore - rs.LScore # New columns to help us iteratively update elos
rs['w_elo'] = None
rs['l_elo'] = None
rs['Result'] = None
rs['elo_diff'] = None

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
	rs.loc[i, 'elo_diff'] = elo_dict[w] - elo_dict[l] #elo_diff before result of game


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
