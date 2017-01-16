'''
Replay saved data through a virtual port.
Created on 26 May 2016

@author: matthew oppenheim
replays accelerometer data from a .txt file
file data format:
counter delta acc_x acc_y acc_z
uses the delta to set the time for the next line of data to be sent
output:
b'START 76649 10001 -0.3162842 0.4382324 -0.9157715 END\r\n'
 To set up a connected pair of serial ports:
socat -d -d pty,raw,echo=0,link=/tmp/ttyV0 pty,raw,echo=0,link=/tmp/ttyV1
 Set SERIAL_PORT to be one of the /tmp/ttyV<x> pair created.
 The data will be o/p on the other.
To monitor o/p: gtkterm -p /tmp/ttyV1

To do:
pack data
option to loop file when it gets to the end
'''

import numpy as np
import os
import pyboard.accelerometer_data_structure as ads
from pyboard import serial_utilities
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph.ptime import time
import pyboard.utilities as utilities
from serial.serialutil import SerialException
import struct
import sys
import pyboard.utilities

BAUD = 115200
PACKER = ads.PACKER
SERIAL_PORT = '/tmp/ttyV0'
TEST_FILE = '/home/matthew/documents/infolab2/projects/hand_gesture/gui_data/2016_05_24_testing_Beaumont/Jack_hand/jack_2.txt'
# frequency to transmit data in Hz
TRANSMIT_FREQ = 2

class ReplayData():
    ''' replay saved data through a virtual serial port '''
    def __init__(self, input_file):
        self.app = QtGui.QApplication([])
        self.frequency = TRANSMIT_FREQ
        print('instigated replay_data')
        self.input_file = TEST_FILE
        self.initialise_generator(self.input_file)
        #self.check_skipped(self.data_file_object)
        self.acc_structure = ads.acc_data_structure
        self.delta = 0
        self.serial_connection = serial_utilities.serial_connect(SERIAL_PORT, BAUD)
        if not self.serial_connection:
            utilities.exit_code('no serial connection')
        self.last_time = time()
        self.interval = 1
        self.counter = 1
        timer = QtCore.QTimer()
        timer.timeout.connect(lambda: self.timeout_handler(timer))
        # timer units are milliseconds. timer.start(0) to go as fast as practical.
        timer.start(1000/self.frequency)
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_'):
            QtGui.QApplication.instance().exec_()

    def calc_frequency(self, delta):
        ''' update the transmission frequency '''
        frequency = 1000000/delta
        return frequency

    def check_skipped(self, in_file):
        ''' see if any counts are missing '''
        counter = 0
        old_counter = 0
        for line in in_file:
            old_counter = counter
            counter, delta, x_acc, y_acc, z_acc = (float(d) for d in line.split())
            counter = int(counter)
            delta = int(delta)
            count_increment = counter-old_counter
            if count_increment !=1:
                print('skipped {} counts at {}'.format(count_increment, counter))

    def file_generator(self, file_object):
        ''' creates a generator to return each line of the file '''
        for line in file_object:
            yield line
        file_object.close()
        print('end of file')

    def get_scan(self):
        ''' get next scan and assign types hhfff'''
        try:
            single_scan = next(self.data_file_generator).split()
        except StopIteration as e:
            print('file end reached')
            self.initialise_generator(self.input_file)
            return
        single_scan[0:2] = [int(x) for x in single_scan[0:2]]
        single_scan[2:5] = [float(x) for x in single_scan[2:5]]
        return single_scan
    
    def initialise_generator(self, input_file):
        ''' open data file as a generator '''
        print('reading from: {}'.format(input_file))
        self.data_file_object = self.open_file(input_file)
        self.data_file_generator = self.file_generator(self.data_file_object)
        
    def scan_to_ads_format(self, single_scan):
        ''' adds start and end identifiers to a scan '''
        single_scan.insert(0,ads.SCAN_START)
        single_scan.append(ads.SCAN_END)
        return single_scan

    def open_file(self, file_path):
        ''' return a file object '''
        try:
            open_file = open(file_path, 'r')
        except Exception as e:
            print('error opening {}:/n{}'.format(file_path, e))
            sys.exit()
        return open_file

    def pack_scan(self, scan_data):
        ''' return packed scan_data '''
        packed = struct.pack(PACKER, *scan_data)
        return packed

    def timeout_handler(self, timer):
        ''' send data to the serial port and adjust timeout frequency '''
        single_scan = self.get_scan()
        try:
            # convert to Acc_scan namedtuple
            acc_scan = self.acc_structure(*single_scan)
        except TypeError as e:
            print('*** scan: {} error: {}'.format(single_scan, e))
            return
        # recover sampling frequency from the delta
        delta_ms = int(acc_scan.delta)/1000
        # set update frequency to the recorded data frequency
        timer.setInterval(delta_ms)
        if not single_scan:
            print('*** no scan')
            return
        packed_scan = self.pack_scan(self.scan_to_ads_format(single_scan))
        try:
            serial_utilities.write(packed_scan, self.serial_connection)
        except SerialException as e:
            print('Could not open serial port, try\nsocat -d -d pty,raw,echo=0,link=/tmp/ttyV0 pty,raw,echo=0,link=/tmp/ttyV1')
            utilities.exit_code('\n error message {}'.format(e))

if __name__ == '__main__':
    replay_data = ReplayData(TEST_FILE)
