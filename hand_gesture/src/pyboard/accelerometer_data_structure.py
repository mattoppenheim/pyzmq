'''
Created on 31 Dec 2015
accelerometer data structure
@author: matthew
'''

import collections
import numpy as np

AMPLITUDE = 2
DISPLAY_SENDER = 'display_sender'
DISPLAY_SIGNAL= 'display_signal'
FRAMES_PER_SECOND = 30
GESTURE_SENDER = 'gesture_sender'
GESTURE_SIGNAL = 'gesture_signal'
NUM_SAMPLES = 300
PORT_SENDER = 'port_sender'
PORT_SIGNAL = 'port_signal'
PYBOARD_SENDER = 'sensor_sender'
SENSOR_SIGNAL_ACC = 'sensor_signal_acc'
WRITE_PYBOARD='write_pyboard'
PACKER = '2shhfff2s'
SCAN_START = b'ST'
SCAN_END =  b'EN'
ZMQ_PORT = '5556'

acc_data_structure = collections.namedtuple('Acc_scan', 'counter, delta, x_acc, y_acc, z_acc')
acc_data_headers = ['counter', 'delta', 'x_acc', 'y_acc', 'z_acc']

def initialise_array(rows=NUM_SAMPLES, cols=1):
    ''' Create a numpy array of 0s. '''
    return np.zeros((rows,cols))


