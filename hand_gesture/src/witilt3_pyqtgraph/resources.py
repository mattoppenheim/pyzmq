'''
constants and resource modules
Created on 20 Aug 2015

@author: matthew
'''
import time, sys
from time import strftime
from  datetime import datetime

SIGNAL_FROM_GUI = 'signal_from_gui'
SIGNAL_FROM_BOARD = 'signal_from_board'
NUM_SAMPLES = 300
G_MAX = 3
G_MIN = -3
R_MAX = 3
R_MIN = -3

def exit_code(message):
    print (message)
    print ("End program")
    sys.exit() # end cleanly

def now_time():
    '''Returns the local time as a string.'''
    now = datetime.now()
    return now.strftime("%H:%M:%S.%f")

def get_time():
    ''' Returns the local time as a datetime. '''
    return datetime.now()