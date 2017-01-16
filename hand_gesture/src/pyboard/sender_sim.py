#!/usr/bin/env python
''' modified from https://github.com/mba7/SerialPort-RealTime-Data-Plotter
simulates accelerometer data:
START counter delta acc_x acc_y acc_z END
b'START 76649 10001 -0.3162842 0.4382324 -0.9157715 END\r\n'
 To set up a connected pair of serial ports:
socat -d -d pty,raw,echo=0,link=/tmp/ttyV0 pty,raw,echo=0,link=/tmp/ttyV1
 Set SERIAL_PORT to be one of the /tmp/ttyV<x> pair created.
 The data will be o/p on the other.
To monitor o/p: gtkterm -p /tmp/ttyV1
command line:
python3 /home/matthew/git/pyboard/src/graph_accelerometer/sender_sim.py
data rate = TRANSMIT_FREQ

'''

import random, math
import numpy as np
import serial
import struct
import sys
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph.ptime import time
from serial.serialutil import SerialException
#import graph_accelerometer.utilities
#import utilities
import pyboard.utilities as utilities
import pyboard.accelerometer_data_structure as ads

# how many samples to average over to measure the transmission frequency
FREQ_AVG = 1000
# frequency to transmit data in Hz
TRANSMIT_FREQ = 100
SERIAL_PORT = '/tmp/ttyV0'
BAUD = 115200
AMPLITUDE=1
PACKER = ads.PACKER
START = ads.SCAN_START
END = ads.SCAN_END

def timefunc(f):
    ''' from https://zapier.com/engineering/profiling-python-boss/
    for profiling methods'''
    def f_timer(*args, **kwargs):
        start = time.time()
        result = f(*args, **kwargs)
        end = time.time()
        print(f.__name__, 'took', end - start, 'time')
        return result
    return f_timer

class sender_sim():
    ''' Sends simulated test data through a virtual serial port. '''
    def __init__(self):
        print('instigated sender_sim')
        self.app = QtGui.QApplication([])
        self.delta = 0
        self.serial_connection = self.serial_connect(SERIAL_PORT, BAUD)
        self.last_time = time()
        self.freq = None
        self.freq_list = np.ones(FREQ_AVG)
        self.interval = 1
        self.counter = 1
        timer = QtCore.QTimer()
        timer.timeout.connect(self.update_acc_data)
        # timer units are milliseconds. timer.start(0) to go as fast as practical.
        timer.start(1000/TRANSMIT_FREQ)
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_'):
            QtGui.QApplication.instance().exec_()

    def create_acc_data(self):
        ''' create the simulated accelerometer data '''
        x = float(random.randint(1, 2)*AMPLITUDE*(math.sin(self.delta)))
        y = float(random.randint(1, 2)*AMPLITUDE*(math.sin(self.delta)))
        z = float(random.randint(1, 2)*AMPLITUDE*(math.sin(self.delta)))
        self.delta += 2*math.pi/TRANSMIT_FREQ
        if self.delta >= 2 * math.pi:
            self.delta = 0
        simulated_data = (START, self.counter, int(1000000*self.interval), x, y, z, END)
        #print('simulated_data: {}'.format(simulated_data))
        self.counter += 1
        return(simulated_data)

    def serial_connect(self, serial_port, baud):
        ''' Return a serial port connection. '''
        print('Trying to connect to serial port: {}'.format(serial_port))
        try:
            new_serial = serial.Serial(serial_port, baud, rtscts=True,dsrdtr=True)
        except SerialException as e:
            print('Could not open serial port, try\nsocat -d -d pty,raw,echo=0,link=/tmp/ttyV0 pty,raw,echo=0,link=/tmp/ttyV1')
            utilities.exit_code('\n error message {}'.format(e))
        new_serial.flushInput()
        print('Serial port {} set up with baud {} and signal frequency {}Hz'.format(new_serial.name, new_serial.baudrate, TRANSMIT_FREQ))
        return new_serial

    #@timefunc
#     def serial_write(self, ch ,serial):
#         ''' writes a character to <serial>  '''
#         ch = str(ch) + ' '
#         serial.write(str(ch).encode('utf-8'))
#         #print('wrote: {}'.format(ch))
#         serial.flush()

    def serial_write(self, message ,serial):
        ''' writes a character to <serial>  '''
        serial.write(message)
        serial.flush()

    def update_freq_list(self):
        ''' Updates freq_list to keep track of the update frequency '''
        now_time = time()
        self.interval = now_time - self.last_time
        self.last_time = now_time
        if self.freq is None:
            self.freq = 1.0/self.interval
        else:
            s = np.clip(self.interval*3., 0, 1)
            self.freq = self.freq * (1-s) + (1.0/self.interval) * s
        self.freq_list[-1] = self.freq


    def update_acc_data(self):
        ''' update the output simulated accelerometer data '''
        self.update_freq_list()
        simulated_data = self.create_acc_data()
        packed = struct.pack(PACKER, *simulated_data)
        self.serial_write(packed, self.serial_connection)

        #print('{:0.1f} averaged freq'.format(FREQ_AVG*np.average(self.freq_list)))


if __name__ == '__main__':
    sender_sim = sender_sim()
    #===========================================================================
    # timer = QtCore.QTimer()
    # timer.timeout.connect(sender_sim.update_acc_data)
    # # timer units are milliseconds. timer.start(0) to go as fast as practical.
    # timer.start(1000/TRANSMIT_FREQ)
    # if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_'):
    #     QtGui.QApplication.instance().exec_()
    #===========================================================================

