import csv
import os
import re
import unittest

import requests
import requests_cache
import update_classes_gms as ucg


class UpdateClasses(unittest.TestCase):
    def setUp(self):
        requests_cache.install_cache('scheduling',
                                     backend='sqlite', expire_after=7200)
        self.first_page, self.status = ucg.get_class_page(ucg.CLASS_URL)
        self.assertEqual(200, self.status)

    def test_can_get_first_page(self):
        next_button = self.first_page.find(id='searchNxtBtn')
        next_url_hint = next_button['onclick']
        self.assertTrue(next_url_hint.startswith('location.href'))

        previous_button = self.first_page.find(id='searchBckBtn')
        previous_url_hint = previous_button['onclick']
        self.assertTrue(previous_url_hint.startswith('history.go'))

    def test_find_table(self):
        self.assertTrue(ucg.find_table(self.first_page))

    def test_find_table_headers(self):
        table = ucg.find_table(self.first_page)
        self.assertEqual(ucg.find_table_headers(table),
                         ['Course',
                          'Title',
                          'Open seats',
                          'Credits',
                          'Day',
                          'Time',
                          'Location',
                          'Instructor'])

    def test_get_table_data(self):
        table = ucg.find_table(self.first_page)
        table_data = ucg.get_table_data(table)
        first_cell = table_data[0][0]
        self.assertTrue(first_cell.startswith('CHEM'))

    def test_get_next_url(self):
        current_url = ucg.CLASS_URL
        next_url = ucg.get_next_url(self.first_page, current_url)
        next_page, status = ucg.get_class_page(next_url)
        self.assertEqual(200, status)

    def test_process_pages(self):
        current_url = ucg.CLASS_URL
        current_page, status = ucg.get_class_page(current_url)
        current_table = ucg.find_table(current_page)
        data = []
        ucg.process_pages(current_page, current_table, current_url, data)
        first_enrollment = data[0][0][2]
        enrollment = re.compile('\d+ OF \d+')
        result = enrollment.search(first_enrollment)
        print result.group()
        self.assertRegexpMatches(first_enrollment, enrollment)

    def test_scrape_pages(self):
        current_url = ucg.CLASS_URL
        headers, data = ucg.scrape_pages(current_url)
        self.assertEqual(headers,
                         ['Course',
                          'Title',
                          'Open seats',
                          'Credits',
                          'Day',
                          'Time',
                          'Location',
                          'Instructor'])
        first_enrollment = data[0][0][2]
        enrollment = re.compile('\d+ OF \d+')
        result = enrollment.search(first_enrollment)
        print result.group()
        self.assertRegexpMatches(first_enrollment, enrollment)

    def test_convert_page_data(self):
        current_url = ucg.CLASS_URL
        headers, data = ucg.scrape_pages(current_url)
        converted_data = ucg.convert_page_data(data)
        first_enrollment = converted_data[0][2]
        enrollment = re.compile('\d+ OF \d+')
        result = enrollment.search(first_enrollment)
        print result.group()
        self.assertRegexpMatches(first_enrollment, enrollment)

    def test_save_csv(self):
        headers = ['a', 'b']
        data = [[3, 7], [11, 13]]
        ucg.save_csv(headers, data, 'test.csv')
        results = open('test.csv')
        results_reader = csv.reader(results)
        results_data = list(results_reader)
        print results_data
        self.assertEqual(results_data,
                         [['a', 'b'],
                          ['3', '7'],
                          ['11', '13']])
        os.remove('test.csv')
