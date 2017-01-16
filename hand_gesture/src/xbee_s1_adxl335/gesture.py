'''
Created on 2 Nov 2016
creates and handles the gesture to be matched
uses gesture_dict to describe the gesture parameters
parameters to be tested for passed in *args, e.g. pitch, roll, acc
@author: matthew
'''

import logging
from gesture_description.gesture_dict import GestureDict

class Gesture():

    def __init__(self, *args):
        self.gesture_dict = GestureDict()
        logging.basicConfig(level=logging.DEBUG, format='%(message)s')
        logging.info('gesture created')
        if 'roll' in args:
            self.test_roll = True
        if 'pitch' in args:
            self.test_pitch = True
        if 'acc' in args:
            self.test_acc = True
        
    def test_acc(self, acc):
        if self.gesture_dict['acc_min'] <= acc <= self.gesture_dict['acc_max']:
            return True
        else:
            return False
    
    def test_roll(self, roll):
        if self.gesture_dict['roll_min'] <= roll <= self.gesture_dict['roll_max']:
            return True
        else:
            return False

    def test_pitch(self, pitch):
        if self.gesture_dict['pitch_min'] <= pitch <= self.gesture_dict['pitch_max']:
            return True
        else:
            return False
        
    def update_gesture(self, new_gesture):
        self.gesture = new_gesture
        logging.info('updated gesture with\n{}'.format(new_gesture))
        