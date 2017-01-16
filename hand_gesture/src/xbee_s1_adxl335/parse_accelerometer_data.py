'''
Created on 22 Dec 2015

@author: matthew
process accelerometer data being read from pyboard
input data is of form

START counter acc_x acc_y acc_z END

parses data into a row and adds this row to a numpy array
The START and END are used to split the scans into single scans.
The START and END are removed from each scan.
The scan is split using a named tuple 'acc_data_structure'.
columns of the numpy array are:
'counter', 'delta', 'x_acc', 'y_acc', 'z_acc'
'''
import xbee_s1_adxl335.accelerometer_data_structure as ads
import numpy as np
import xbee_s1_adxl335.utilities as utilities
from nltk.metrics.scores import precision

class Parse_accelerometer_data():
    ''' parse accelerometer data read from pyboard '''

    def __init__(self, start='START', end='END', delta=100000):
        self.old_counter = False
        self.start = start
        self.end = end
        self.num_data_fields = 7
        # delta is the time between scans
        self.time_delta = delta
        self.partial_scan = None
        self.Acc_scan = ads.acc_data_structure
        headers = ads.acc_data_headers
        # data is held in a numpy array of size number samples x number of data columns
        self.scans_array = np.array(ads.initialise_array(cols = len(headers)))
        print('scans_array.shape: {}'.format(self.scans_array.shape))
        print('data headers: {}'.format(ads.acc_data_headers))
        self.remap = {ord('\r'):None,ord('\n'):None}

    def add_data_array(self, array, sample):
        ''' add sample to the end of an array '''
        array[:-1] = array[1:]
        array[-1] = sample
        return array

    def check_counter(self, counter):
        ''' check the counter has incremented correctly '''
        counter_delta = int(counter)-self.old_counter
        if counter_delta != 1:
            print('*** counter delta is {}'.format(counter_delta))

    def check_delta(self, delta):
        ''' check that the time between scans is in spec '''
        if int(delta) > self.time_delta + 100:
            print('*** delta is {}'.format(delta))

    def extract_scan(self, multi_scans, start_marker, end_marker):
        ''' return a single scan and the multi_scans-single scan '''
        start = multi_scans.index(start_marker) + len(start_marker)
        end = multi_scans.index(end_marker, start)
        single_scan =  multi_scans[start:end]
        multi_scans = multi_scans[end+len(end_marker):]
        return multi_scans, single_scan

    def get_acc_data(self):
        return(self.scans_array)

    def parse_data(self, scan):
        ''' parse all of the data '''
        scan = scan.decode()
        # previous scan was the start of a partial scan
        if self.partial_scan:
            scan=str(self.partial_scan+scan)
        while True:
            try:
                scan, single_scan = self.extract_scan(scan, self.start, self.end)
                self.parse_single_scan(single_scan)
            except ValueError:
                # any partial scan at the end gets tacked on to the next scan
                self.partial_scan=scan
                break

    def parse_single_scan(self, scan):
        ''' parse a single scan into a named tuple, then append to data array '''
        try:
            self.acc_scan = self.Acc_scan(*scan.split())
        except TypeError as e:
            utilities.exit_code('scan: {} error: {}'.format(scan, e))
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
        #np.set_printoptions(suppress=True, precision=4, formatter={'float':'{: 8}'.format})
        #print(self.scans_array[-1:])

if __name__ == '__main__':
    parse = Parse_accelerometer_data()
