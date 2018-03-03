import pandas as pd

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

def prepare_data(detailed_season_results_path):
	'''
	Returns dataframe that is suitable for performing group by.
	It cleans any data to make it suitable for further processing
	:param detailed_season_results_path:
	:return:
	'''
	# Load the season results
	seasons_results = pd.read_csv(detailed_season_results_path)

	# Create a copy and rearrange column data
	seasons_results_copy = seasons_results.copy()
	seasons_results_copy[['WTeamID', 'WScore', 'WFGM', 'WFGA','WFGM3', 'WFGA3', 'WFTM', 'WFTA',	'WOR', 'WDR', 'WAst', 'WTO', 'WStl', 'WBlk', 'WPF']] = seasons_results[['LTeamID', 'LScore', 'LFGM', 'LFGA','LFGM3', 'LFGA3', 'LFTM', 'LFTA', 'LOR', 'LDR', 'LAst', 'LTO', 'LStl', 'LBlk', 'LPF']]
	seasons_results_copy[
		['LTeamID', 'LScore', 'LFGM', 'LFGA', 'LFGM3', 'LFGA3', 'LFTM', 'LFTA', 'LOR', 'LDR', 'LAst', 'LTO', 'LStl',
		 'LBlk', 'LPF']] = seasons_results[
		['WTeamID', 'WScore', 'WFGM', 'WFGA', 'WFGM3', 'WFGA3', 'WFTM', 'WFTA', 'WOR', 'WDR', 'WAst', 'WTO', 'WStl',
		 'WBlk', 'WPF']]

	seasons_results_concat = pd.concat([seasons_results, seasons_results_copy], ignore_index=True)

	# Rename the columns
	seasons_results_concat.rename(columns={
		'WTeamID': 'TeamID_1',
		'WScore': 'Score_1',
		'LTeamID': 'TeamID_2',
		'LScore': 'Score_2',
		# Winning team
		'WFGM': 'FGM_1',
		'WFGA': 'FGA_1',
		'WFGM3': 'FGM3_1',
		'WFGA3': 'FGA3_1',
		'WFTM': 'FTM_1',
		'WFTA': 'FTA_1',
		'WOR': 'OR_1',
		'WDR': 'DR_1',
		'WAst': 'Ast_1',
		'WTO': 'TO_1',
		'WStl': 'Stl_1',
		'WBlk': 'Blk_1',
		'WPF': 'PF_1',
		# Losing team
		'LFGM': 'FGM_2',
		'LFGA': 'FGA_2',
		'LFGM3': 'FGM3_2',
		'LFGA3': 'FGA3_2',
		'LFTM': 'FTM_2',
		'LFTA': 'FTA_2',
		'LOR': 'OR_2',
		'LDR': 'DR_2',
		'LAst': 'Ast_2',
		'LTO': 'TO_2',
		'LStl': 'Stl_2',
		'LBlk': 'Blk_2',
		'LPF': 'PF_2'
	}, inplace=True)

	return seasons_results_concat

def get_poss(tm_FGA, tm_FGM, tm_FTA, tm_OR, tm_DR, tm_TO, opp_FGA, opp_FGM, opp_FTA, opp_OR, opp_DR, opp_TO):
	tm_half = tm_FGA + 0.4*tm_FTA - 1.07*(tm_OR / (tm_OR + opp_DR))*(tm_FGA - tm_FGM) + tm_TO
	opp_half = opp_FGA + 0.4*opp_FTA - 1.07*(opp_OR / (opp_OR + tm_DR))*(opp_FGA - opp_FGM) + opp_TO
	return 0.5*(tm_half+opp_half)

def get_ORtg(points, poss):
	return 100 * points / poss

def get_DRtg(opp_points_allowed, poss):
	return 100 * opp_points_allowed / poss

def get_season_totals(data):
	season_team_totals = data.groupby(['Season', 'TeamID_1']).agg({
		'Score_1': {
			'GP': 'count',
			'Score_1': 'sum'
		},
		'Score_2': 'sum',
		'FGM_1': 'sum',
		'FGA_1': 'sum',
		'FGM3_1': 'sum',
		'FGA3_1': 'sum',
		'FTM_1': 'sum',
		'FTA_1': 'sum',
		'OR_1': 'sum',
		'DR_1': 'sum',
		'Ast_1': 'sum',
		'TO_1': 'sum',
		'Stl_1': 'sum',
		'Blk_1': 'sum',
		'PF_1': 'sum',
		'FGM_2': 'sum',
		'FGA_2': 'sum',
		'FGM3_2': 'sum',
		'FGA3_2': 'sum',
		'FTM_2': 'sum',
		'FTA_2': 'sum',
		'OR_2': 'sum',
		'DR_2': 'sum',
		'Ast_2': 'sum',
		'TO_2': 'sum',
		'Stl_2': 'sum',
		'Blk_2': 'sum',
		'PF_2': 'sum'
	}).reset_index()
	season_team_totals.columns = ['Season', 'TeamID_1', 'GP', 'Score_1', 'Score_2', 'FGM_1', 'FGA_1', 'FGM3_1',
								  'FGA3_1', 'FTM_1', 'FTA_1', 'OR_1', 'DR_1', 'Ast_1', 'TO_1',
								  'Stl_1', 'Blk_1', 'PF_1', 'FGM_2', 'FGA_2', 'FGM3_2', 'FGA3_2', 'FTM_2', 'FTA_2',
								  'OR_2', 'DR_2', 'Ast_2',
								  'TO_2', 'Stl_2', 'Blk_2', 'PF_2']
	return season_team_totals

def get_four_factors(tm_FGA, tm_FGM, tm_FGM3, tm_FTA, tm_FTM, tm_TO, tm_OR, opp_DR):

	# Shooting the ball
	efg = (tm_FGM + 0.5*tm_FGM3)/tm_FGA

	# Taking care of the ball
	turnover_rate = tm_TO / (tm_FGA + 0.44 * tm_FTA + tm_TO)

	# Offensive rebounding
	offensive_rebounding_percentage = tm_OR / (tm_OR + opp_DR)

	# Free throw rate
	free_throw_rate = tm_FTM / tm_FGA

	return 0.4 * efg + 0.25 + turnover_rate + 0.2 * offensive_rebounding_percentage + 0.15 * free_throw_rate


def get_advanced_statistics(data):
	'''
	Returns data in the format:
	| Season | TeamID | Poss | OffRtg | DefRtg |

	Note: Currently inefficient
	:param data:
	:return: advanced statistics for teams in a season
	'''

	# Calculate season totals for each team by season
	season_team_totals = get_season_totals(data)

	# Calculate advanced statistics
	# Calculate possessions for each team
	season_team_totals['Total_Poss'] = season_team_totals.apply(lambda season_team_total: get_poss(
		season_team_total['FGA_1'],
		season_team_total['FGM_1'],
		season_team_total['FTA_1'],
		season_team_total['OR_1'],
		season_team_total['DR_1'],
		season_team_total['TO_1'],
		season_team_total['FGA_2'],
		season_team_total['FGM_2'],
		season_team_total['FTA_2'],
		season_team_total['OR_2'],
		season_team_total['DR_2'],
		season_team_total['TO_2']
	), axis=1)

	# Calculate avg poss for a team
	season_team_totals['Poss'] = season_team_totals.apply(lambda season_team_stat: season_team_stat['Total_Poss'] / season_team_stat['GP'], axis=1)

	# Calculate offensive and defensive ratings
	season_team_totals[['OffRtg', 'DefRtg']] = season_team_totals.apply(lambda season_team_stat: pd.Series({'OffRtg': get_ORtg(season_team_stat['Score_1'], season_team_stat['Total_Poss']), 'DefRtg': get_DRtg(season_team_stat['Score_2'], season_team_stat['Total_Poss'])}), axis=1)

	# Calculate net rating
	season_team_totals['NetRtg'] = season_team_totals.apply(lambda season_team_stat: season_team_stat['OffRtg'] - season_team_stat['DefRtg'], axis=1)

	# Calculate four factors
	season_team_totals['FourFactors'] = season_team_totals.apply(lambda season_team_stat: get_four_factors(season_team_stat['FGA_1'], season_team_stat['FGM_1'], season_team_stat['FGM3_1'], season_team_stat['FTA_1'], season_team_stat['FTM_1'], season_team_stat['TO_1'], season_team_stat['OR_1'], season_team_stat['DR_2']), axis=1)

	# Start to build team season advanced stats and extract relevant columns only
	season_team_advanced_stats = season_team_totals[['Season', 'TeamID_1', 'Poss', 'OffRtg', 'DefRtg', 'NetRtg', 'FourFactors']].copy()

	# Rename column
	season_team_advanced_stats.rename(columns={'TeamID_1': 'TeamID'}, inplace=True)

	return season_team_advanced_stats

data = prepare_data('input/RegularSeasonDetailedResults.csv')
advanced_stats = get_advanced_statistics(data)
print(advanced_stats)