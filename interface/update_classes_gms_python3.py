import re

import pandas as pd
import requests
from bs4 import BeautifulSoup

CLASS_URL = ("https://udapps.nss.udel.edu/CoursesSearch/search-results"
             "?term=2198"  # enter current term here
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

SEMESTER = "S2021"


# for future refactor: automatically compute semester code
def semester_code(semester):
    """Given a year, return the corresponding semester code.

    Args:
        semester (str): the semester in format "X2nnn". X = W/S/J/F; 2nnn is
        the year.

    Returns:
        (int): the code.
    """
    year = int(semester[1:])
    if not 2000 <= year < 2100:
        print('ERROR year must be from 2000 to 2099')
        return None
    season = semester[0]
    if season not in ['W', 'S', 'J', 'F']:
        print(
            'ERROR first letter for session is invalid (must be W, S, J, or F)')
        return None
    season_code = {'W': '1',
                   'S': '3',
                   'J': '5',
                   'F': '8'}
    code = '2' + semester[-2:] + season_code[season]
    return code


def class_url(semester):
    """
    Return a class URL for a semester.

    Parameters
    ----------
    semester : in format "X20nn" e.g. S2020, J2019

    Returns
    -------
    (string) URL for the corresponding semester
    """
    term = semester_code(semester)
    url = ("https://udapps.nss.udel.edu/CoursesSearch/search-results"
           "?term="  # enter current term here
           + term
           +
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
    return url


def get_class_page(url):
    response = requests.get(url, headers=HEADERS)
    return BeautifulSoup(response.content, 'lxml'), response.status_code


def find_table(page):
    return page.find_all('table')[0]


def find_table_headers(table):
    # return [th.text.encode('ascii') for th in table.select('th')]
    return [th.text for th in table.select('th')]

def get_table_data(table):
    """Parse a bs4 table selection row by row to return a list of lists.
        :param: table: bs4 table element
        :returns: a list of lists of td elements, analogous to a list of
        spreadsheet rows"""
    table_rows = table.select('tr')
    table_data = [[td.text.strip() for td in row.select('td')]
                  for row in table_rows[1:]]
    lab_dis_data = [[td.text.strip()
                     for td in row.select('td')]
                    for row in table_rows[1:] if is_lab_or_dis(row)]
    return table_data, lab_dis_data


def is_lab_or_dis(tr):
    coursetype = tr.find_all('span')
    return coursetype[0].string == 'LAB' or coursetype[0].string == 'DIS'


def get_next_url(page, current_url):
    next_button = page.find(id='searchNxtBtn')
    if next_button is None:
        print('end reached')
        return None
    print('current url: ', current_url)
    next_url_hint = next_button['onclick']
    startat = re.compile('&startat=[^&\']*')
    print('searching: ', next_url_hint)
    new_startat = startat.search(next_url_hint).group()
    print('new startat: ', new_startat)

    new_url = startat.sub(new_startat, current_url)
    print('new url: ', new_url)
    return new_url


def process_pages(current_page, current_table, current_url, data):
    full_data, lab_dis_data = get_table_data(current_table)
    data[0].append(full_data)
    data[1].append(lab_dis_data)
    new_url = get_next_url(current_page, current_url)
    if new_url is None:
        return
    else:
        print('old url: ', current_url[-25:])
        print('new_url: ', new_url[-25:])
        new_page, status = get_class_page(new_url)
        new_table = find_table(new_page)
        process_pages(new_page, new_table, new_url, data)


def scrape_pages(current_url):
    current_page, status = get_class_page(current_url)
    all_data = [[], []]
    #     at_end = False
    current_table = find_table(current_page)
    headers = find_table_headers(current_table)
    print('headers: ', headers)
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


def test_url():
    """temp test to make sure new url function consistent with old"""
    assert CLASS_URL == class_url('F2019')

if __name__ == '__main__':
    test_url()
    current_url = class_url(SEMESTER)
    headers, data = scrape_pages(current_url)
    full_data = convert_page_data(data[0])
    lab_dis_data = convert_page_data(data[1])
    full_filename = SEMESTER + '_full.csv'
    lab_dis_filename = SEMESTER + '_lab_dis.csv'
    save_csv(headers, full_data, full_filename)
    save_csv(headers, lab_dis_data, lab_dis_filename)
