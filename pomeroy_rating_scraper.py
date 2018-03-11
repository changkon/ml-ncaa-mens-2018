import scrapy


class PomeroyRatingScraper(scrapy.Spider):
    name = "pomeroy_rating_spider"

    start_urls = [
        "https://kenpom.com/index.php?y=2003",
        "https://kenpom.com/index.php?y=2004",
        "https://kenpom.com/index.php?y=2005",
        "https://kenpom.com/index.php?y=2006",
        "https://kenpom.com/index.php?y=2007",
        "https://kenpom.com/index.php?y=2008",
        "https://kenpom.com/index.php?y=2009",
        "https://kenpom.com/index.php?y=2010",
        "https://kenpom.com/index.php?y=2011",
        "https://kenpom.com/index.php?y=2012",
        "https://kenpom.com/index.php?y=2013",
        "https://kenpom.com/index.php?y=2014",
        "https://kenpom.com/index.php?y=2015",
        "https://kenpom.com/index.php?y=2016",
        "https://kenpom.com/index.php?y=2017",
    ]

    def parse(self, response):
        # result = response.xpath('//table[@id="ratings-table"]').extract()
        sel = response.selector

        div = sel.css("div#content-header")
        header_text = div.xpath('h2/text()').extract()
        print(header_text[0][:4])

        season = header_text[0][:4]

        for tr in sel.css("table#ratings-table>tbody>tr"):
            # print(tr)
            a_element = tr.xpath('td/a/text()').extract()
            print(a_element)
            team_name = a_element[0]

            text_elements = tr.xpath('td/text()').extract()
            print(text_elements)

            adj_o_rating = text_elements[4]
            adj_d_rating = text_elements[5]
            adj_tempo = text_elements[6]

            yield {
                'Season': season,
                'TeamName': team_name,
                'AdjORating': adj_o_rating,
                'AdjDRating': adj_d_rating,
                'AdjTempo': adj_tempo
            }
