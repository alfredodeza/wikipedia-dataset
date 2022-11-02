import scrapy

import os
from os.path import dirname

current_dir = os.path.dirname(__file__)
print(f"current dir: {current_dir}")
top_dir = dirname(dirname(dirname(current_dir)))
print(f"top dir {top_dir}")
url = os.path.join(top_dir, "html/1992_World_Junior_Championships_in_Athletics_–_Men's_high_jump")
sql_file = os.path.join(top_dir, 'sql_files/populate.sql')


start_urls = []
for file in os.listdir(os.path.join(top_dir, "html")):
    path = os.path.join(top_dir, "html", file)
    start_urls.append(f"file://{path}")

# Make sure that the interesting data is available. Interesting data means we have finalists and all the other athletes.
def find_finalists_table(response):
    for table in response.xpath('//table'):
        body = table.xpath('tbody')
        # check if len of body is more than 12, otherwise skip it
        if len(body.xpath('tr')) < 12:
            continue
        # now check if we have medalists
        for tr in body.xpath('tr'):
            if tr.xpath('td/span/img/@alt').extract_first():
                return table


class MedalistsSpider(scrapy.Spider):
    name = 'medalists'
    allowed_domains = ['wikipedia.org']
    start_urls = start_urls

    def parse(self, response):
        table = find_finalists_table(response)
        results = []
        # extract the year from the title
        year = response.xpath('//title/text()').extract_first().split()[0]

        for tr in table.xpath('tbody').xpath('tr'):
            # extract the text value of alt attribute of the img tag
            medal = tr.xpath('td/span/img/@alt').extract_first()
            if medal and "medalist" in medal:
                place = medal.split()[0]
            else:
                try:
                    place, _ = tr.xpath('td/text()').extract()
                except ValueError:
                    pass
            try:
                athlete = tr.xpath('td/a/text()').extract_first()
            except ValueError:
                pass
        
            if not athlete and not medal:
                continue
            height = tr.xpath('td/b/text()').extract_first()
            
            #results.append([place, athlete, height, year])
            append_sql_file(place, athlete, height, year)
        #print(results)


def append_sql_file(place, athlete, height, year):
    line = f"INSERT INTO medalists(place, athlete, height, year) VALUES ('{place}', '{athlete}', '{height}', '{year}');\n"
    if not os.path.exists(sql_file):
        with open(sql_file, 'w') as _f:
            _f.write(line)
        return
    with open(sql_file, 'a') as _f:
        _f.write(line)
