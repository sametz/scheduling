import re

import pandas as pd
import requests
from bs4 import BeautifulSoup

CLASS_URL = ("https://udapps.nss.udel.edu/CoursesSearch/search-results"
             "?term=2183"
             "&search_type=A"
             "&course_sec=CHEM"
             "&session=All"
             "&course_title="
             "&instr_name="
             "&text_info=All"
             "&instrtn_mode=All"
             "&time_start_hh="
             "&time_start_ampm="
             "&credit=Any"
             "&keyword="
             "&subj_area_code="
             "&college="
             "&startat="
             )
HEADERS = {'User-Agent': 'Mozilla/5.0'}


def get_class_page(url):
    response = requests.get(url, headers=HEADERS)
    return BeautifulSoup(response.content, 'lxml'), response.status_code


def find_table(page):
    return page.find_all('table')[0]


def find_table_headers(table):
    return [th.text.encode('ascii') for th in table.select('th')]


def get_table_data(table):
    """Parse a bs4 table selection row by row to return a list of lists.
        :param: table: bs4 table element
        :returns: a list of lists of td elements, analogous to a list of spreadsheet rows"""
    table_rows = table.select('tr')
    table_data = [[td.text.strip().encode('ascii') for td in row.select('td')]
                  for row in table_rows[1:]]
    return table_data


def get_next_url(page, current_url):
    next_button = page.find(id='searchNxtBtn')
    if next_button is None:
        print 'end reached'
        return None
    print 'current url: ', current_url
    next_url_hint = next_button['onclick']
    startat = re.compile('&startat=[^&\']*')
    print 'searching: ', next_url_hint
    new_startat = startat.search(next_url_hint).group()
    print 'new startat: ', new_startat

    new_url = startat.sub(new_startat, current_url)
    print 'new url: ', new_url
    return new_url


def process_pages(current_page, current_table, current_url, data):
    data.append(get_table_data(current_table))
    new_url = get_next_url(current_page, current_url)
    if new_url == None:
        return
    else:
        print 'old url: ', current_url[-25:]
        print 'new_url: ', new_url[-25:]
        new_page, status = get_class_page(new_url)
        new_table = find_table(new_page)
        process_pages(new_page, new_table, new_url, data)


def scrape_pages(current_url):
    current_page, status = get_class_page(current_url)
    all_data = []
    #     at_end = False
    current_table = find_table(current_page)
    headers = find_table_headers(current_table)
    print 'headers: ', headers
    process_pages(current_page, current_table, current_url, all_data)

    return headers, all_data


def convert_page_data(data):
    result = []
    for page in data:
        for row in page:
            result.append(row)
    return result


def save_csv(headers, data, filename):
    df = pd.DataFrame.from_records(data, columns=headers)
    df.to_csv(filename, index=False)


if __name__ == '__main__':
    current_url = CLASS_URL
    headers, data = scrape_pages(current_url)
    good_data = convert_page_data(data)
    save_csv(headers, good_data, 'test_spring18.csv')