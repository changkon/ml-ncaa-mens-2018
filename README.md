# ml-ncaa-mens-2018
Use python 3.6

Necessary libraries:
* pandas
* numpy
* scikit-learn

## Input Data
Place input data in input folder

## Results
| Season | Data Type | Stats | Log Loss |
| ------ | --------- | ----- | -------- |
| 2003-2013 | Regular Season | ORtg, DRtg, Seed Diff | 0.542679214062 |
| 2003-2013 | Regular Season | ORtg, DRtg, NetRtg, FourFactors, Seed Diff | 0.542104885388 |
| 2010-2013 | Regular Season | ORtg, DRtg, Seed Diff | 0.549534941948 |
| 2010-2013 | Regular Season | ORtg, DRtg, NetRtg, FourFactors, Seed Diff | 0.549105422882 |

## Strategies
1. Use single season data only as NCAA has one and done rule. Since team roster will vary a lot, there is no point training only several seasons.
2. Include advanced statistics for best players in each respective team. As basketball is heavily influenced by "superstars", it makes sense to include advanced statistics of the best players for training