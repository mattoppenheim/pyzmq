'''
Created on 12 May 2016

@author: matthew oppenheim

unpack accelerometer data adxl335 sent via xbee_s1_adxl335
stand alone utility

'''
import accelerometer_data_structure as ads
import fnmatch
import logging
import math
import numpy as np
import os
from pydispatch import dispatcher
from struct import *
import struct
import serial
import sys
import time
from xbee import XBee


BAUD = 115200
# fake delta for testing, time between samples
DELTA = 10000
PYBOARD_SIGNAL_ACC = 'sensor_signal_acc'

g = lambda x: (x-512)/102.4

class Xbee_Connect():
    def __init__(self, delta=100000, serial_connection=None):
        self.logger = logging.getLogger()
        self.logger.debug('Xbee_Connect instigated')
        self.counter = 0
        self.old_counter = False
        self.partial_scan = None
        self.scan_length = 22
        headers = ads.acc_data_headers
        # scans_array is the numpy array that holds the accelerometer scans, ads format
        # plus one extra column for absolute value 
        self.scans_array = np.array(ads.initialise_array(cols = len(headers)+1))
        self.time_delta = delta
        dispatcher.connect(self.dispatcher_receive, signal=ads.DISPLAY_SIGNAL, sender=ads.DISPLAY_SENDER)
        self.Acc_scan = ads.acc_data_structure
        if not serial_connection:
            serial_port = self.find_xbee_port()
        try:
            xbee_connection = self.xbee_connection(BAUD, serial_port)
        except AttributeError as e:
            self.exit_code('no serial connection found, error code: \n{}'.format(e))  
        self.get_bytes(xbee_connection)
        
    def check_counter(self, counter):
        ''' check the counter has incremented correctly '''
        counter_delta = int(counter)-self.old_counter
        if counter_delta != 1:
            self.logger.debug('*** counter delta is {}'.format(counter_delta))

    def check_delta(self, delta):
        ''' check that the time between scans is in spec '''
        if int(delta) > self.time_delta + 100:
            self.logger.debug('*** delta is {}'.format(delta))

    def dispatcher_receive(self, message):
        ''' Handle received dispatches. '''
        if message == 'send_data':
            dispatcher.send(signal=PYBOARD_SIGNAL_ACC, sender=ads.PYBOARD_SENDER,
                            message=self.get_acc_data())  
        
    def exit_code(self, message):
        self.logger.debug (message)
        self.logger.debug ("End program")
        sys.exit() # end cleanly
    
           
    def find_xbee_port(self):
        ''' returns the port that the xbee  is connected to '''
        # look for a xbee connected to a /dev/ttyACM<n> port
        ttymodems = fnmatch.filter(os.listdir('/dev'), 'ttyUSB*')
        xbee_port = False
        if ttymodems:
            xbee_port = '/dev/' + ttymodems[0]
            self.logger.debug('xbee port is {}'.format(xbee_port))
            return(xbee_port)
        # look for simulated data on /tmp/ttyV1
        ttymodems=fnmatch.filter(os.listdir('/tmp'), 'tty*')
        if ttymodems:
            xbee_port = '/tmp/'+ ttymodems[1]
            self.logger.debug('*** using simulated data')
            self.logger.debug('xbee port is {}'.format(xbee_port))
            return(xbee_port)
        if not xbee_port:
            self.exit_code('Error: no xbee found.')

    def get_acc_data(self):
        ''' return the accelerometer data, which is a numpy array '''
        return(self.scans_array)
               
    def get_bytes(self, xbee_connection, num_bytes = None):
        '''Returns all waiting data from the open serial port.'''
        while (1):
            try:
                read_bytes = xbee_connection.wait_read_frame()
            except IndexError as e:
                self.logger.debug(e)
            if read_bytes:
                self.counter += 1
                x, y, z = self.parse_acc_data(read_bytes)
                abs = math.sqrt(x**2+y**2+z**2)
                new_array_row = np.array([self.counter,DELTA,x,y,z,abs],dtype=float)
                self.scans_array = np.vstack((self.scans_array,new_array_row))
                self.scans_array = np.delete(self.scans_array, (0), axis=0)
            # without a sleep command, this thread will suck the cpu time and bottleneck the plotting
            time.sleep(0.002)

    def parse_acc_data(self, xbee_scan):
        ''' return accelerometer data '''
        adc_dict=xbee_scan['samples'][0]
        return g(adc_dict['adc-0']), g(adc_dict['adc-1']), g(adc_dict['adc-2'])
                 
    def parse_single_scan(self, single_scan):
        ''' parse a single scan into a named tuple, then append to data array '''
        try:
            # convert to Acc_scan namedtuple 
            self.acc_scan = self.Acc_scan(*single_scan)
        except TypeError as e:
            self.exit_code('scan: {} error: {}'.format(single_scan, e))
        if not self.old_counter:
            self.old_counter = int(self.acc_scan.counter)
            self.logger.debug('initialised old_counter')
        self.check_delta(self.acc_scan.delta)
        self.check_counter(self.acc_scan.counter)
        self.old_counter = int(self.acc_scan.counter)
        new_array_row = np.array([self.acc_scan.counter, self.acc_scan.delta, \
            self.acc_scan.x_acc, self.acc_scan.y_acc, self.acc_scan.z_acc],dtype=float)
        self.scans_array = np.vstack((self.scans_array,new_array_row))
        self.scans_array = np.delete(self.scans_array, (0), axis=0)
        
    def xbee_connection(self, baud, serial_port):
        ''' Return the xbee serial port connection. '''
        self.logger.debug('Trying to connect to serial port: {}'.format(serial_port))
        try:
            xbee_connection = XBee(serial.Serial(serial_port, baud), escaped=True)
        except serial.SerialException as e:
            self.logger.debug('self.serial error {}'.format(e))
        self.logger.debug('Serial port {} set up with baud {}'.format(serial_port, baud))
        return xbee_connection

if __name__ == '__main__':
    xbee = Xbee_Connect()
    