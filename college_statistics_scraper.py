import scrapy

class CollegeStatisticsScraper(scrapy.Spider):
    name = "college_statistics_spider"
    start_urls = [
        "https://basketball.realgm.com/ncaa/players/2018/A",
        "https://basketball.realgm.com/ncaa/players/2018/B",
        "https://basketball.realgm.com/ncaa/players/2018/C",
        "https://basketball.realgm.com/ncaa/players/2018/D",
        "https://basketball.realgm.com/ncaa/players/2018/E",
        "https://basketball.realgm.com/ncaa/players/2018/F",
        "https://basketball.realgm.com/ncaa/players/2018/G",
        "https://basketball.realgm.com/ncaa/players/2018/H",
        "https://basketball.realgm.com/ncaa/players/2018/I",
        "https://basketball.realgm.com/ncaa/players/2018/J",
        "https://basketball.realgm.com/ncaa/players/2018/K",
        "https://basketball.realgm.com/ncaa/players/2018/L",
        "https://basketball.realgm.com/ncaa/players/2018/M",
        "https://basketball.realgm.com/ncaa/players/2018/N",
        "https://basketball.realgm.com/ncaa/players/2018/O",
        "https://basketball.realgm.com/ncaa/players/2018/P",
        "https://basketball.realgm.com/ncaa/players/2018/Q",
        "https://basketball.realgm.com/ncaa/players/2018/R",
        "https://basketball.realgm.com/ncaa/players/2018/S",
        "https://basketball.realgm.com/ncaa/players/2018/T",
        "https://basketball.realgm.com/ncaa/players/2018/U",
        "https://basketball.realgm.com/ncaa/players/2018/V",
        "https://basketball.realgm.com/ncaa/players/2018/W",
        "https://basketball.realgm.com/ncaa/players/2018/X",
        "https://basketball.realgm.com/ncaa/players/2018/Y",
        "https://basketball.realgm.com/ncaa/players/2018/Z"
    ]


    def parse(self, response):
        for link in response.css('.main.wrapper table tbody tr>td:first-child a ::attr(href)').extract():
            if link is not None:
                next_page = response.urljoin(link)
                yield scrapy.Request(next_page, callback=self.parseStatistics)
    
    def parseStatistics(self, response):
        # extract player name
        player_name_unfiltered = response.css('.profile-box .half-column-left h2 ::text').extract_first()
        player_name = player_name_unfiltered.replace(u'\xa0', u'')

        # Cycle through tables to find the ones for NCAA. It has School in 2nd column and Class in 3rd column
        stats_tables = response.css('.profile-wrap table')
        index = 1
        for stats_table in stats_tables:
            try:
                column_2 = stats_table.css('thead tr th:nth-of-type(2) ::text').extract_first()
                column_3 = stats_table.css('thead tr th:nth-of-type(3) ::text').extract_first()

                if column_2 == 'School' and column_3 == 'Class':
                    break
                else:
                    index = index + 1
            except Exception:
                pass

        # extract per game statistic which is the first table
        season_per_game_statistics_selector = '.profile-wrap table:nth-of-type(' + str(index) + ') tbody tr'
        season_per_game_statistics = response.css(season_per_game_statistics_selector)

        season_advanced_statistics_selector = '.profile-wrap table:nth-of-type(' + str((index + 3)) + ') tbody tr'
        season_advanced_statistics = response.css(season_advanced_statistics_selector)
        season_advanced_statistics_iter = iter(season_advanced_statistics)

        # Cycle through seasons
        for per_game_statistic in season_per_game_statistics:
            # Cycle through next advanced
            advanced_statistic = next(season_advanced_statistics_iter)

            season = per_game_statistic.css('td:nth-of-type(1) ::text').extract_first()
            school = per_game_statistic.css('td:nth-of-type(2) a ::text').extract_first()
            if school is None:
                school = per_game_statistic.css('td:nth-of-type(2) ::text').extract_first()
            minutes_per_game = per_game_statistic.css('td:nth-of-type(6) ::text').extract_first()

            # Get raw stats
            points_per_game = per_game_statistic.css('td:nth-of-type(24) ::text').extract_first()
            assists_per_game = per_game_statistic.css('td:nth-of-type(19) ::text').extract_first()
            rebounds_per_game = per_game_statistic.css('td:nth-of-type(18) ::text').extract_first()
            steals_per_game = per_game_statistic.css('td:nth-of-type(20) ::text').extract_first()
            blocks_per_game = per_game_statistic.css('td:nth-of-type(21) ::text').extract_first()

            # Get advanced stats
            player_oRating = advanced_statistic.css('td:nth-of-type(18) ::text').extract_first()
            player_dRating = advanced_statistic.css('td:nth-of-type(19) ::text').extract_first()
            player_per = advanced_statistic.css('td:nth-of-type(20) ::text').extract_first()

            yield {
                'Season': season,
                'School': school,
                'Name': player_name,
                'Min': minutes_per_game,
                'Pts': points_per_game,
                'Ast': assists_per_game,
                'Reb': rebounds_per_game,
                'Stl': steals_per_game,
                'Blk': blocks_per_game,
                'ORtg': player_oRating,
                'DRtg': player_dRating,
                'Per': player_per
            }