import unittest

import requests
import requests_cache
import update_classes_gms as ucg


class UpdateClasses(unittest.TestCase):
    def setUp(self):
        requests_cache.install_cache('scheduling', \
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

