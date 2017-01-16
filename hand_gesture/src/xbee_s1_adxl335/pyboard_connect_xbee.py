'''
Created on 30 Oct 2015
@author: matthew
Finds and displays data from a pyboard on /dev/ACM*
Handles partial scans and multiple scans
ST and EN markers surround the scans
get_bytes repeatedly polls for new data
data is sent using a dispatcher in dispatch_receive
'''


import xbee_s1_adxl335.accelerometer_data_structure as ads
#from xbee_s1_adxl335.parse_accelerometer_data import Parse_accelerometer_data

from struct import *
import xbee_s1_adxl335.accelerometer_data_structure as ads
import xbee_s1_adxl335.serial_utilities as serial_utilities
import struct
import numpy as np
import os
from pydispatch import dispatcher
import serial
import sys
import time
import xbee_s1_adxl335.utilities as utilities

BAUD = 115200
# name of dispatcher signal for dispatches leaving from this class
SIGNAL_FROM_PYBOARD = 'signal_from_serial'
# name of dispatcher signal for dispatches coming into this class
PYBOARD_SIGNAL_ACC = 'sensor_signal_acc'
PYBOARD_SIGNAL_HEADERS = 'sensor_signal_headers'


class Pyboard_Connect_XBee():
    ''' displays output from a pyboard through the serial port '''

    def __init__(self, start=b'ST', end=b'EN', delta=100000, serial_connection=None):

        print('{} Starting pyboard_connect_xbee'.format(utilities.now_time()))
        if serial_connection:
            self.serial = serial_utilities.serial_connect(serial_connection,BAUD)
        else:
            try:
                self.serial = serial_utilities.serial_connect(BAUD, serial_utilities.find_pyboard())
            except AttributeError as e:
                utilities.exit_code('no serial connection found, error code: \n{}'.format(e))
        dispatcher.connect(self.dispatcher_receive, signal=ads.DISPLAY_SIGNAL, sender=ads.DISPLAY_SENDER)
        dispatcher.connect(self.write_pyboard, signal=ads.WRITE_PYBOARD, sender=ads.DISPLAY_SENDER)
        self.old_counter = False
        self.start_marker = start
        self.end_marker = end
        self.partial_scan = None
        self.scan_length = 22
        headers = ads.acc_data_headers
        self.scans_array = np.array(ads.initialise_array(cols = len(headers)))
        self.time_delta = delta
        self.Acc_scan = ads.acc_data_structure
  
        self.packer = ads.PACKER
        self.get_bytes()
        
    def dispatcher_receive(self, message):
        ''' Handle received dispatches. '''
        if message == 'send_data':
            dispatcher.send(signal=PYBOARD_SIGNAL_ACC, sender=ads.PYBOARD_SENDER,
                            message=self.get_acc_data())    

    def check_counter(self, counter):
        ''' check the counter has incremented correctly '''
        counter_delta = int(counter)-self.old_counter
        if counter_delta != 1:
            print('*** counter delta is {}'.format(counter_delta))

    def check_delta(self, delta):
        ''' check that the time between scans is in spec '''
        if int(delta) > self.time_delta + 100:
            print('*** delta is {}'.format(delta))
    
    def extract_scan(self, multi_scans):
        ''' return a single scan and the multi_scans-single scan '''
        start = multi_scans.index(self.start_marker)
        end = multi_scans.index(self.end_marker)
        single_scan =  multi_scans[start:end+len(self.end_marker)]
        # check for an incomplete scan - another start marker before an end marker
        while (self.start_marker in single_scan[len(self.start_marker):]):
            single_scan=self.fix_single_scan(single_scan)
        multi_scans = multi_scans[end+len(self.end_marker):]
        return multi_scans, single_scan

    def fix_single_scan(self, single_scan):
        print('fixing')
        print('input: {}'.format(single_scan))
        single_scan = single_scan[len(self.start_marker):]  
        start = single_scan.index(self.start_marker)  
        single_scan = single_scan[start:]
        print('output: {}'.format(single_scan))
        return single_scan
    
    def get_acc_data(self):
        ''' return the accelerometer data, which is a numpy array '''
        return(self.scans_array)
               
    def get_bytes(self,num_bytes = None):
        '''Returns all waiting data from the open serial port.'''
        while (1):
            inWaiting = self.serial.inWaiting()
            read_bytes = self.serial.read(inWaiting)
            if read_bytes:
                self.parse_data(read_bytes)
                # for testing, enable the print function below to see data being read from pyboard
                #print(read_bytes)
            # without a sleep command, this thread will suck the cpu time and bottleneck the plotting
            time.sleep(0.002)

    def parse_data(self, multi_scans):
        ''' parse all of the data '''
        # previous scan was the start of a partial scan
        if self.partial_scan:
            multi_scans=self.partial_scan+multi_scans
        while True:
            try:
                multi_scans, single_scan = self.extract_scan(multi_scans)
                self.parse_single_scan(single_scan)
            # partial string will raise a ValueError as missing the end character
            except ValueError as e:
                # any partial scan at the end gets tacked on to the next scan
                self.partial_scan=multi_scans
                break   
                 
    def parse_single_scan(self, single_scan):
        ''' parse a single scan into a named tuple, then append to data array '''
        try:
            single_scan = unpack(self.packer,single_scan)
            # remove start and end markers
            single_scan = single_scan[1:-1]           
        except struct.error as e:
            print('caught: {} for {}'.format(e, single_scan))
            return
        try:
            # convert to Acc_scan namedtuple 
            self.acc_scan = self.Acc_scan(*single_scan)
        except TypeError as e:
            utilities.exit_code('scan: {} error: {}'.format(single_scan, e))
        if not self.old_counter:
            self.old_counter = int(self.acc_scan.counter)
            print('initialised old_counter')
        self.check_delta(self.acc_scan.delta)
        self.check_counter(self.acc_scan.counter)
        self.old_counter = int(self.acc_scan.counter)
        new_array_row = np.array([self.acc_scan.counter, self.acc_scan.delta, \
            self.acc_scan.x_acc, self.acc_scan.y_acc, self.acc_scan.z_acc],dtype=float)
        self.scans_array = np.vstack((self.scans_array,new_array_row))
        self.scans_array = np.delete(self.scans_array, (0), axis=0)

    def write_pyboard(self, message):
        ''' sends data to the pyboard '''
        serial_utilities.write(bytes(message, 'utf-8'), self.serial)
        
if __name__ == '__main__':
    pyboard = Pyboard_Connect()