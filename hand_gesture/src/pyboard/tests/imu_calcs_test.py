'''
Created on 4 Apr 2016

@author: matthew
'''
import pyboard.imu_calcs as ic
import unittest


class Test(unittest.TestCase):

    def test_get_pitch_returns_correct_value(self):
        self.assertAlmostEqual(15.50136, ic.get_pitch(1, 2, 3), places=3)
        pass

    def test_get_roll_returns_correct_value(self):
        self.assertAlmostEqual(32.3115, ic.get_roll(1, 2, 3),places=3)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()