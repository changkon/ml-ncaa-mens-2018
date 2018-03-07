import sklearn.metrics as metrics
import pandas as pd

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

def simulate_submit(submission):
    '''
    Tests submission prediction for playoff games between 2014-2017 against actual playoff results.
    This is a local function which is the same as the one the stage 1 submission in kaggle.
    Submission should be a dataframe that has columns so it has the following structure
    | ID | Pred |
    Aim for SMALLER log loss
    :param submission:
    :return: log loss
    '''
    # Load playoff data
    compact_playoff_results = pd.read_csv("input/NCAATourneyCompactResults.csv")

    # create a local function to meausre the logloss so don't have submit every time
    val_start_year = 2014
    val_end_year = 2017

    val_results = compact_playoff_results.loc[
        (compact_playoff_results['Season'] >= val_start_year) & (compact_playoff_results['Season'] <= val_end_year)]
    val_results = val_results.loc[val_results['DayNum'] >= 136]
    val_results = val_results.drop(['DayNum', 'WScore', 'LScore', 'WLoc', 'NumOT'], axis=1)

    val_results['ID'] = val_results.apply(create_id, axis=1)
    val_results['Result'] = val_results.apply(get_result, axis=1)
    val_results = val_results.drop(['WTeamID', 'LTeamID'], axis=1)

    final_comparison = submission.merge(val_results, on='ID')

    for target_season in final_comparison.Season.unique():
        temp = final_comparison[ final_comparison['Season'] == target_season]
        print('Season ', target_season, ' log loss: ', metrics.log_loss(temp['Result'], temp['Pred']))

    final_log_loss = metrics.log_loss(final_comparison['Result'], final_comparison['Pred'])
    print('final log loss: ', final_log_loss)

    return final_log_los