'''
Created on 14 Sep 2015
Contains methods for returning data from a Sparkfun witilt3 board.

Witilt3 data format=
b'#@ xSH xSL xXH xXL xYH xYL xZH xZL xBL xBH xRH xRL$

SH=sample high, XH=x acc. high, BH=battery high, RH=gyro high
splits the socket data into chunks of length witilt3_constants.LENGTH_SCAN
 - change this if sensors are disabled

Send '1' to get witilt menu
Send 'S' to start binary data collection
Send 'A' to abort binary data collection

Cribbed parts from Sparkfun witilt example

@author: matthew
'''
START_BYTE = b'#@'
END_BYTE = b'$'

from  datetime import datetime
from time import strftime
import witilt3_constants


def now_time():
    '''returns the local time as a string'''
    now = datetime.now()
    return now.strftime("%H:%M:%S.%f")

class Witilt3_Device():
    # complete witilt3 data scan
    complete_scan = bytes()

    def __init__(self):
        print('Instigated Witilt3_Device')

    def add_two_bytes(self, data_low, data_high):
        ''' Add two bytes. '''
        return data_high*256 + data_low

    def assemble_scans(self, new_data):
        ''' Assembles multiple or partial witilt3 data scans into complete scans. '''
        # if no data, return
        if not new_data:
            return
        # start of an incomplete scan, save to append with next scan
        if new_data.startswith(START_BYTE) and len(new_data) < self.sensor_board.get_length_scan():
            self.complete_scan = new_data
            ('{} short data, appending with next: {}'.format(now_time(), new_data))
            return
        # data scan, with a beginning and end symbol - may be multiple scans
        if new_data.startswith(START_BYTE) and new_data.endswith(END_BYTE):
            self.complete_scan = bytes()
            return(new_data)
        # end of an incomplete scan
        if new_data.endswith(END_BYTE):
            data_to_return = (self.complete_scan+new_data)
            # reset complete_scan to be empty for the next scan
            self.complete_scan = bytes()
            return data_to_return
        # No start or end detected. Probably 'b'#' detected.
        else:
            self.complete_scan = self.complete_scan + new_data
            return

    def get_count(self, scan):
        ''' Return count data from a data scan. '''
        return self.add_two_bytes(scan[witilt3_constants.COUNT_LOW], scan[witilt3_constants.COUNT_HIGH])

    def get_x_acc(self, scan):
        ''' Return x accelerometer data from a data scan. '''
        return self.add_two_bytes(scan[witilt3_constants.X_LOW], scan[witilt3_constants.X_HIGH])

    def get_y_acc(self, scan):
        ''' Return y accelerometer data from a data scan. '''
        return self.add_two_bytes(scan[witilt3_constants.Y_LOW], scan[witilt3_constants.Y_HIGH])

    def get_z_acc(self, scan):
        ''' Return z accelerometer data from a data scan. '''
        return self.add_two_bytes(scan[witilt3_constants.Z_LOW],scan[witilt3_constants.Z_HIGH])

    def get_gyro(self, scan):
        ''' Return gyro data from a data scan. '''
        return self.add_two_bytes(scan[witilt3_constants.R_LOW], scan[witilt3_constants.R_HIGH])

    def get_length_scan(self):
        ''' Returns the length of the data scan. '''
        return witilt3_constants.LENGTH_SCAN

    def split_scan(self, current_scan):
        ''' Splits the witilt3 data into single scans. '''

        # if no data, return
        if not current_scan:
            return
        # trim off /x00 from start of scan string
        current_scan=self.trim_scan(current_scan)

        # split data into single scan lengths
        # sometimes multiple scans are returned, so split on characters between scans '$#'
        scans = current_scan.split(START_BYTE)
        for scan in scans:
            # if no data in the scan
            if not scan:
                continue
            scan = bytes(scan)
            # debugging print statement
            #print(self.bytes_to_hex(scan))
            if not scan.endswith(END_BYTE):
                print('+++ {} incorrect end byte for {} scans: {} current_scan: {}'.format(now_time(), scan, scans, current_scan))
                continue
            # We have trimmed off the '#@' bytes from the start of the scan
            if len(scan) != self.get_length_scan()-witilt3_constants.TRIMMED:
                print('*** {} incorrect length {} for {} scans: {} current_scan: {}'.format(now_time(), len(scan), scan, scans, current_scan))
                continue
            # return the scans
            return scans


    def trim_scan(self, scan):
        ''' Trim off /x00 from start of scan string '''
        if scan[0] == b'\x00':
            scan = scan[1:]
            return scan

if __name__ == '__main__':
    witilt3 = Witilt3_Device()