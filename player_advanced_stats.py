import pandas as pd

def get_season_formatted(season):
    season_prefix = season[:2]
    season_suffix_end = season[2:]

    season_suffix_start = str(int(season_suffix_end) - 1)
    return season_prefix + season_suffix_start + '-' + season_suffix_end

def get_player_advanced_stats_for_team(df, team_name, season, **kwargs):
    # Retrieve player count
    player_count = kwargs.get('player_count', 1)

    # Get formatted season
    formatted_season = get_season_formatted(season)

    # Filter out values with not populated data
    df = df[(df['Season'] != '-') & (df['School'] != '-') & (df['Name'] != '-') & (df['Min'] != '-') & (df['Pts'] != '-') & (df['Ast'] != '-') & (df['Reb'] != '-') & (df['Stl'] != '-') & (df['Blk'] != '-') & (df['ORtg'] != '-') & (df['DRtg'] != '-') & (df['Per'] != '-') & (df['Usg'] != '-')]

    # Update numeric columns to floats
    numeric_columns = ['Min', 'Pts', 'Ast', 'Reb', 'Stl', 'Blk', 'ORtg', 'DRtg', 'Per', 'Usg']
    df.loc[:,numeric_columns] = df.loc[:,numeric_columns].astype(float)

    # Select rows whose team name equals provided team name
    # Filter out scrubs
    season_player_team_stats = df[(df['School'] == team_name) & (df['Season'] == formatted_season) & (df['Min'].astype(float) > 25.0)]

    # Order the players by usage rate. This is to find most important players
    season_player_team_stats_ordered = season_player_team_stats.sort_values(by='Usg', ascending=False)

    # Get top players
    top_players = season_player_team_stats_ordered.head(player_count)
    print(top_players)

    # Get stats to sum up
    adv_stats_columns = ['ORtg', 'DRtg', 'Per']

    player_advanced_stats_for_team = top_players[adv_stats_columns].sum()

    return tuple(player_advanced_stats_for_team)

data = pd.read_csv('2018-player-usg.csv')
adv_stats = get_player_advanced_stats_for_team(data, "Georgetown", "2018", player_count=2)
print(adv_stats)