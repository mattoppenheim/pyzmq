'''
Created on 30 Oct 2015
@author: matthew
Finds and displays data from a pyboard on /dev/ACM*
'''


import xbee_s1_adxl335.accelerometer_data_structure as ads
from xbee_s1_adxl335.parse_accelerometer_data import Parse_accelerometer_data
import fnmatch
import os
from pydispatch import dispatcher
import serial
import sys
import time
import xbee_s1_adxl335.serial_utilities as serial_utilities
import xbee_s1_adxl335.utilities as utilities


BAUD = 115200
# name of dispatcher signal for dispatches leaving from this class
SIGNAL_FROM_PYBOARD = 'signal_from_serial'
# name of dispatcher signal for dispatches coming into this class
PYBOARD_SIGNAL_ACC = 'sensor_signal_acc'
PYBOARD_SIGNAL_HEADERS = 'sensor_signal_headers'


class Pyboard_Connect_Wire():
    ''' displays output from a pyboard through the serial port '''

    def __init__(self, serial_connection=None):

        print('{} Starting pyboard_connect_wire'.format(utilities.now_time()))
        if serial_connection:
            self.serial = serial_utilities.serial_connect(serial_connection,BAUD)
        else:
            try:
                self.serial = serial_utilities.serial_connect(serial_utilities.find_pyboard(), BAUD)
            except AttributeError as e:
                utilities.exit_code('no serial connection found, error code: \n{}'.format(e))
        try:
            self.serial = serial_utilities.serial_connect(serial_utilities.find_pyboard(),BAUD)
        except AttributeError as e:
            utilities.exit_code('no serial connection found, error code: \n{}'.format(e))
        self.parsed_data = Parse_accelerometer_data()
        dispatcher.connect(self.dispatcher_receive, signal=ads.DISPLAY_SIGNAL, sender=ads.DISPLAY_SENDER)
        dispatcher.connect(self.write_pyboard, signal=ads.WRITE_PYBOARD, sender=ads.DISPLAY_SENDER)
        self.get_bytes()
        
    def dispatcher_receive(self, message):
        ''' Handle received dispatches. '''
        #print('dispatch received by pyboard_receive: {} '.format(str(message)))
        if message == 'send_data':
            dispatcher.send(signal=PYBOARD_SIGNAL_ACC, sender=ads.PYBOARD_SENDER,
                            message=self.get_acc_data())         
    
    def get_acc_data(self):
        ''' returns the accelerometer data '''
        return self.parsed_data.get_acc_data()

    def get_bytes(self,num_bytes = None):
        '''Returns all waiting data from the open serial port.'''
        while (1):
            inWaiting = self.serial.inWaiting()
            read_bytes = self.serial.read(inWaiting)
            if read_bytes:
                self.parsed_data.parse_data(read_bytes)
                # for testing, enable the print function below to see data being read from pyboard
                #print(read_bytes)
            # without a sleep command, this thread will suck the cpu time and bottleneck the plotting
            time.sleep(0.002)

    def write_pyboard(self, message):
        ''' sends data to the pyboard '''
        serial_utilities.write(bytes(message, 'utf-8'), self.serial)
        
if __name__ == '__main__':
    pyboard = Pyboard_Connect()