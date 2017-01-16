'''
Created on 12 May 2016

@author: matthew oppenheim

unpack accelerometer data mcu6050 sent via xbee_s1_adxl335
data format is set in self.packer
stand alone utility

'''
import accelerometer_data_structure as ads
import fnmatch
import numpy as np
import os
from struct import *
import struct
import serial
import time
import sys

BAUD = 115200

class Xbee_Connect():
    def __init__(self, start=b'ST', end=b'EN', delta=100000):
        print('started')
        self.old_counter = False
        self.start_marker = start
        self.end_marker = end
        self.partial_scan = None
        self.scan_length = 22
        headers = ads.acc_data_headers
        self.scans_array = np.array(ads.initialise_array(cols = len(headers)))
        self.time_delta = delta
        self.Acc_scan = ads.acc_data_structure
        try:
            self.serial_connect(BAUD)
        except AttributeError as e:
            self.exit_code('no serial connection found, error code: \n{}'.format(e))  
        self.packer = ('2shhfff2s')
        self.get_bytes()
        
    def check_counter(self, counter):
        ''' check the counter has incremented correctly '''
        counter_delta = int(counter)-self.old_counter
        if counter_delta != 1:
            print('*** counter delta is {}'.format(counter_delta))

    def check_delta(self, delta):
        ''' check that the time between scans is in spec '''
        if int(delta) > self.time_delta + 100:
            print('*** delta is {}'.format(delta))
        
    def exit_code(self, message):
        print (message)
        print ("End program")
        sys.exit() # end cleanly
    
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
           
    def find_pyboard(self):
        ''' returns the port that the pyboard is connected to '''
        # look for a pyboard connected to a /dev/ttyACM<n> port
        ttymodems = fnmatch.filter(os.listdir('/dev'), 'ttyUSB*')
        pyboard_port = False
        if ttymodems:
            pyboard_port = '/dev/' + ttymodems[0]
            print('pyboard port is {}'.format(pyboard_port))
            return(pyboard_port)
        # look for simulated data on /tmp/ttyV1
        ttymodems=fnmatch.filter(os.listdir('/tmp'), 'tty*')
        if ttymodems:
            pyboard_port = '/tmp/'+ ttymodems[1]
            print('*** using simulated data')
            print('pyboard port is {}'.format(pyboard_port))
            return(pyboard_port)
        if not pyboard_port:
            self.exit_code('Error: no pyboard found.')

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
        #scan = scan.decode()
        # previous scan was the start of a partial scan
        if self.partial_scan:
            multi_scans=self.partial_scan+multi_scans
            #print('self.partial detected, multi_scans is:\n{}'.format(multi_scans))
        while True:
            try:
                multi_scans, single_scan = self.extract_scan(multi_scans)
                self.parse_single_scan(single_scan)
            # partial string will raise a ValueError as missing the end character
            except ValueError as e:
                #print('ValueError: {} multi_scans {}'.format(e, multi_scans))
                # any partial scan at the end gets tacked on to the next scan
                self.partial_scan=multi_scans
                break   
                 
    def parse_single_scan(self, single_scan):
        ''' parse a single scan into a named tuple, then append to data array '''
        try:
            #print('single_scan: {} length {}'.format(single_scan, len(single_scan)))
            single_scan = unpack(self.packer,single_scan)
            # remove start and end markers
            single_scan = single_scan[1:-1]
            print(single_scan)            
        except struct.error as e:
            print('caught: {} for {}'.format(e, single_scan))
            return
        try:
            # convert to Acc_scan namedtuple 
            self.acc_scan = self.Acc_scan(*single_scan)
        except TypeError as e:
            self.exit_code('scan: {} error: {}'.format(single_scan, e))
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
        
    def serial_connect(self, baud):
        ''' Set up the serial port connection. '''
        serial_port = self.find_pyboard()
        print('Trying to connect to serial port: {}'.format(serial_port))
        try:
            self.serial = serial.Serial(serial_port, baud)
        except serial.SerialException as e:
            print('self.serial error {}'.format(e))
        self.serial.flushInput()
        print('Serial port {} set up with baud {}'.format(serial_port, baud))

if __name__ == '__main__':
    xbee = Xbee_Connect()
    