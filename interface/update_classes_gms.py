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


if __name__ == '__main__':
    current_url = CLASS_URL