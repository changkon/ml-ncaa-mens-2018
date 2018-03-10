import pandas as pd

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

pomeroy_rating = pd.read_csv("pomeroy_rating.csv")
teams = pd.read_csv("input/Teams.csv")

print(pomeroy_rating.dtypes)
print(pomeroy_rating.shape)
print(pomeroy_rating.head())

# AdjDRating    float64
# Season          int64
# AdjTempo      float64
# AdjORating    float64
# TeamName       object

# somehow halfway the columns order are swapped so i have to split the dataframe and rearrange the bottom half
# to get it in the right order again
top_half = pomeroy_rating.iloc[:5126, :]

bottom_half = pomeroy_rating.iloc[5126:, :].iloc[1:, :]
bottom_half = bottom_half[['AdjORating', 'TeamName', 'AdjDRating', 'Season', 'AdjTempo']]
bottom_half = bottom_half.rename(columns={
    'AdjORating': 'TeamName',
    'TeamName': 'AdjTempo',
    'AdjDRating': 'AdjORating',
    'AdjTempo': 'AdjDRating'
})
pomeroy_rating = pd.concat([top_half, bottom_half], ignore_index=True)

# need to cast the type to number because the incorrect column order caused these value to be made string
pomeroy_rating['AdjDRating'] = pd.to_numeric(pomeroy_rating['AdjDRating'])
pomeroy_rating['AdjORating'] = pd.to_numeric(pomeroy_rating['AdjORating'])
pomeroy_rating['Season'] = pd.to_numeric(pomeroy_rating['Season'])
pomeroy_rating['AdjTempo'] = pd.to_numeric(pomeroy_rating['AdjTempo'])


def team_name_from_pomeroy(name):
    name = name.strip('.')
    name = name.replace('Saint ', 'St ')
    name = name.replace('St. ', 'St ')

    name = name.replace('Eastern ', 'E ')

    if name == 'North Carolina St':
        return 'NC State'
    elif name == "Milwaukee":
        return 'WI Milwaukee'
    elif name == "Kent St":
        return "Kent"
    elif name == "Western Michigan":
        return "W Michigan"
    elif name == "Southern Illinois":
        return "S Illinois"
    elif name == "St Mary's":
        return "St Mary's CA"
    elif name == "St Joseph's":
        return "St Joseph's PA"
    elif name == "Northwestern St":
        return "Northwestern LA"
    elif name == "George Washington":
        return "G Washington"
    elif name == "Northern Illinois":
        return "N Illinois"
    elif name == "Albany":
        return "Albany NY"
    elif name == "Sacramento St":
        return "CS Sacramento"
    elif name == "Central Connecticut":
        return "Connecticut"
    elif name == "American":
        return "American Univ"
    elif name == "Boston University":
        return "Boston Univ"
    elif name == "Western Carolina":
        return "W Carolina"
    elif name == "Troy St":
        return "Troy"
    elif name == "Texas A&M Corpus Chris":
        return "Texas A&M"
    elif name == "Southern":
        return "Southern Univ"
    elif name == "Monmouth":
        return "Monmouth NJ"
    elif name == "South Carolina St":
        return "S Carolina St"
    elif name == "Western Illinois":
        return "W Illinois"
    elif name == "UMKC":
        return "Missouri KC"
    elif name == "UTSA":
        return "UT San Antonio"
    elif name == "UC Santa Barbara":
        return "Santa Barbara"
    elif name == "The Citadel":
        return "Citadel"
    elif name == "Southwest Texas St":
        return "Texas St"
    elif name == "Mount St Mary's":
        return "Mt St Mary's"
    elif name == "LIU Brooklyn":
        return "Brooklyn"
    elif name == "Prairie View A&M":
        return "Prairie View"
    elif name == "Green Bay":
        return "WI Green Bay"
    elif name == "Cal Poly":
        return "Cal Poly SLO"
    elif name == "Mississippi Valley St":
        return "Mississippi St"
    elif name == "Grambling St":
        return "Grambling"
    elif name == "Stephen F. Austin":
        return "SF Austin"
    elif name == "Maryland E Shore":
        return "Maryland"
    elif name == "FIU":
        return "Florida Intl"
    elif name == "Southeastern Louisiana":
        return "SE Louisiana"
    elif name == "Loyola Chicago":
        return "Loyola-Chicago"
    elif name == "Loyola Marymount":
        return "Loy Marymount"
    elif name == "Louisiana Lafayette":
        return "ULL"
    elif name == "East Tennessee St":
        return "ETSU"
    elif name == "College of Charleston":
        return "Col Charleston"
    elif name == "Charleston Southern":
        return "Charleston So"
    elif name == "Fairleigh Dickinson":
        return "F Dickinson"
    elif name == "Birmingham Southern":
        return "Birmingham So"
    elif name == "Bethune Cookman":
        return "Bethune-Cookman"
    elif name == "Arkansas Little Rock" or name == "Little Rock":
        return "Ark Little Rock"
    elif name == "Arkansas Pine Bluff":
        return "Ark Pine Bluff"
    elif name == "Southeast Missouri St":
        return "SE Missouri St"
    elif name == "Cal St Northridge":
        return "CS Northridge"
    elif name == "Cal St Fullerton":
        return "CS Fullerton"
    elif name == "Cal St Bakersfield":
        return "CS Bakersfield"
    elif name == "North Carolina A&T":
        return "NC A&T"
    elif name == "Coastal Carolina":
        return "Coastal Car"
    elif name == "Illinois Chicago":
        return "IL Chicago"
    elif name == "Central Michigan":
        return "C Michigan"
    elif name == "Texas Southern":
        return "TX Southern"
    elif name == "Tennessee Martin":
        return "TN Martin"
    elif name == "Florida Atlantic":
        return "FL Atlantic"
    elif name == "VCU":
        return "VA Commonwealth"
    elif name == "Louisiana Monroe":
        return "ULM"
    elif name == "Southwest Missouri St":
        return "Missouri St"
    elif name == "Western Kentucky":
        return "WKU"
    elif name == "Middle Tennessee St" or name == "Middle Tennessee":
        return "MTSU"
    elif name == "Northern Kentucky":
        return "N Kentucky"
    elif name == "Northern Colorado":
        return "N Colorado"
    elif name == "Central Arkansas":
        return "Cent Arkansas"
    elif name == "North Carolina Central":
        return "NC Central"
    elif name == "Houston Baptist":
        return "Houston Bap"
    elif name == "Florida Gulf Coast":
        return "FL Gulf Coast"
    elif name == "Kennesaw St":
        return "Kennesaw"
    elif name == "South Dakota St":
        return "S Dakota St"
    elif name == "Winston Salem St":
        return "W Salem St"
    elif name == "Utah Valley St":
        return "Utah Valley"
    elif name == "SIU Edwardsville":
        return "Edwardsville"
    elif name == "Nebraska Omaha":
        return "NE Omaha"
    elif name == "North Dakota St":
        return "N Dakota St"
    elif name == "UMass Lowell":
        return "MA Lowell"
    elif name == "Abilene Christian":
        return "Abilene Chr"
    elif name == "USC Upstate":
        return "SC Upstate"
    elif name == "UT Rio Grande Valley" or name == "Texas Pan American":
        return "UTRGV"
    elif name == "Georgia Southern":
        return "Ga Southern"
    elif name == "Fort Wayne":
        return "IPFW"

    return name

pomeroy_rating['TeamName'] = pomeroy_rating['TeamName'].apply(team_name_from_pomeroy)

pomeroy_rating = pomeroy_rating.merge(teams, on=["TeamName"], how="left")
pomeroy_rating['AdjNRating'] = pomeroy_rating['AdjORating'] - pomeroy_rating['AdjDRating']
pomeroy_rating = pomeroy_rating.drop(['TeamName', 'FirstD1Season', 'LastD1Season'], axis=1)

# some how there is duplicate, maybe it was the incorrect column order
pomeroy_rating = pomeroy_rating.drop_duplicates(['Season', 'TeamID'])
print(pomeroy_rating.head())
print(pomeroy_rating.isnull().values.any())
print(pomeroy_rating.loc[(pomeroy_rating['TeamID'] == 1107) & (pomeroy_rating['Season'] == 2015)])
pomeroy_rating.to_csv('p_rating_with_team_id.csv', index=False)



