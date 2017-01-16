'''
Created on 14 Jan 2016

@author: matthew
'''

#import graph_accelerometer.accelerometer_data_structure
from graph_accelerometer.parse_accelerometer_data import Parse_accelerometer_data
from io import StringIO
from unittest import TestCase
from unittest.mock import patch
import unittest


class TestParse(TestCase):

    def setUp(self):
        self.parse = Parse_accelerometer_data()

    def tearDown(self):
        pass

    def test_check_delta_returns_correct_result(self):
        test_delta = self.parse.expected_delta + 101
        expected_stdout = '*** delta is {}\n'.format(test_delta)
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.parse.check_delta(test_delta)
            self.assertEqual(fake_out.getvalue(), expected_stdout)

    def test_check_counter_returns_correct_resut(self):
        test_counter = 2
        expected_stdout = '*** counter delta is {}\n'.format(test_counter)
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.parse.check_counter(test_counter)
            self.assertEqual(fake_out.getvalue(), expected_stdout)
            
    def test_check_add__data_array_returns_correct_result(self):
        self.assertEqual([1,2,3], self.parse.add_data_array([0,1,2],3))


if __name__ == "__main__":
    unittest.main()