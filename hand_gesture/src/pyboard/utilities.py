'''
Created on 29 Dec 2015
utility functions

@author: matthew
'''

from datetime import datetime
import numpy as np
import sys

time_list=[]

def now_time():
    '''returns the local time as a string in format %H:%M:%S.%f '''
    now = datetime.now()
    return now.strftime('%H:%M:%S.%f')

def now_time_simple():
    '''returns the local time as a string in format %H:%M:%S '''
    now = datetime.now()
    return now.strftime('%H:%M:%S')

def exit_code(message):
    print (message)
    print ("End program")
    sys.exit() # end cleanly
    
    
