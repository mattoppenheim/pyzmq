'''
Created on 19 Jun 2015

@author: matthew

find and connect with a Sparkfun witilt using serial over the debug port using an FTDI cable

if there is failure to connect, make the owner of rfcomm0 the user that runs this script ***
e.g. sudo chown matthew /dev/rfcomm0

Data format=
b'#@ xSH xSL xXH xXL xYH xYL xZH xZL xBL xBH xRH xRL$

SH=sample high, XH=x acc. high, BH=battery high, RH=gyro high
splits the socket data into chunks of length LENGTH_SCAN - change this if sensors are disabled
Send '1' to get witilt menu
Send 'S' to start binary data collection
Send 'A' to abort binary data collection

Cribbed parts from Sparkfun witilt example
'''
import sys
from time import strftime
from  datetime import datetime
import serial_wiconstants
from pydispatch import dispatcher
from time import sleep
import serial


SIGNAL_FROM_GUI = 'signal_from_gui'
SIGNAL_FROM_BOARD = 'signal_from_board'
#witilt scan has 15 bytes with start byte, x,y,z accelerometer, gyro, battery and count bytes
LENGTH_SCAN = 13
SERIAL_PORT = '/dev/ttyUSB0'
BAUD = 115200
TIMEOUT = 0.2
# How many characters trimmed from start of scan during processing.
TRIMMED = 2

wi_data = bytearray()

start_byte = b'#@'
end_byte = b'$'
# how often we update the gui in seconds
UPDATE_FREQ = 1

def exit_code(message):
    print (message)
    print ("End program")
    sys.exit() # end cleanly

def now_time():
    '''returns the local time as a string'''
    now = datetime.now()
    return now.strftime("%H:%M:%S.%f")


class Serial_Connect():
    ''' Creates a serial connection with a WiTilt through the debug port. '''
    complete_scan = bytes()

    def __init__(self):
        print('{} Starting Serial_Connect'.format(now_time()))
        self.serial_connect(SERIAL_PORT, BAUD)
        # set up dispatcher to enable communication with witilt board
        dispatcher.connect(self.dispatch_from_gui, signal=SIGNAL_FROM_GUI, sender=dispatcher.Any)
        self.last_count_low = 0
        self.previous_widata = bytes()
        self.serial_write('S')
        self.get_bytes()

    def assemble_data(self, new_data):
        ''' Assembles partial witilt data scans into complete scans. '''
        # if no data, return
        if not new_data:
            return
        # start of an incomplete scan, save to append with next scan
        if new_data.startswith(start_byte) and len(new_data) < LENGTH_SCAN:
            self.complete_scan = new_data
            ('{} short data, appending with next: {}'.format(now_time(), new_data))
            return
        # data scan, with a beginning and end symbol
        if new_data.startswith(start_byte) and new_data.endswith(end_byte):
            self.complete_scan = bytes()
            return(new_data)
        # end of an incomplete scan
        if new_data.endswith(end_byte):
            data_to_return = (self.complete_scan+new_data)
            # reset complete_scan to be empty for the next scan
            self.complete_scan = bytes()
            return data_to_return
        # No start or end detected. Probably 'b'#' detected.
        else:
            self.complete_scan = self.complete_scan + new_data
            return

    def bytes_to_hex(self, byte_data):
        ''' returns all the bytes in byte_data as byte code, not the character.'''
        output = ''
        for char in byte_data:
            output += ('{:02x} '.format(char))
        return output

    def dispatch_from_gui(self, message):
        ''' Pydispatch event handler for incoming signals. Sends message to socket. '''
        self.serial_write(message.__str__())

    def get_bytes(self,num_bytes = None):
        '''Returns all data in waiting from the open serial port.'''
        while (1):
            inWaiting = self.serial.inWaiting()
            read_bytes = self.serial.read(inWaiting)
            if read_bytes:
                # uncomment this to interact with witilt configuration menu
                #print(read_bytes)
                #
                self.process_widata(self.assemble_data(read_bytes))

    def process_widata(self, widata):
        ''' Parse and display a complete witilt data scan. '''
        # if no data, return
        if not widata:
            return
        # check that widata is a multiple of complete scans in length
        if widata[0] == 0x0:
            print('trimming data')
            widata = widata[1:]
        #bin first scan with the spurious $#R tagged on
        #widata = widata[LENGTH_SCAN+3:]
        # split witilt data into single scan lengths
        #scans = [widata[i:i+LENGTH_SCAN] for i in range(0, len(widata), LENGTH_SCAN)]
        # sometimes multiple scans are returned, so split on characters between scans '$#'
        scans = widata.split(b'#@')
        for scan in scans:
            # if no data in the scan
            if not scan:
                continue
            scan = bytes(scan)
            #print(self.bytes_to_hex(scan))
            if not scan.endswith(end_byte):
                print('+++ {} incorrect end byte for {} scans: {} widata: {}'.format(now_time(), scan, scans, widata))
                continue
            # We have trimmed off the '#@' bytes from the start of the scan
            if len(scan) != LENGTH_SCAN-TRIMMED:
                print('*** {} incorrect length {} for {} scans: {} widata: {}'.format(now_time(), len(scan), scan, scans, widata))
                continue
            witilt_dict = self.witilt_dict(scan)
            self.count_low = witilt_dict['count_low']
            # 0x0a (new line symbol) not used in low_count location, skips from 0x09 to 0x0b
            if self.count_low - self.last_count_low not in (1, -255) and self.count_low != (0x0b):
                print('### missing {} scans'.format(str(self.count_low - self.last_count_low-1)))
                print(self.bytes_to_hex(self.previous_widata))
                print(self.bytes_to_hex(widata))
            self.last_count_low = self.count_low
            dispatcher.send(signal=SIGNAL_FROM_BOARD, board_data=(witilt_dict))
#             print('count_high {:02x} count_low {:02x} x_high {:02x} x_low {:02x}'
#                    .format(self.count_high, self.count_low, self.x_high, self.x_low))
            #self.periodic_display(self.count_low)

        self.previous_widata = widata

  

    def serial_write(self,ch=' '):
        ''' writes a character into the port and waits TIMEOUT seconds. '''
        self.serial.write(bytes(ch, 'ascii'))
        self.serial.flush()
        print('wrote: {} to board'.format(ch))
        sleep(TIMEOUT)

    def trim_widata(self, widata):
        ''' Trim off /x00 from start of widata string '''
        if widata[0] == b'\x00':
            widata = widata[1:]
            return widata

    def witilt_dict(self, scan):
        ''' Create a dictionary from the witilt data. '''
        witilt_dict = dict()
        witilt_dict['count_low'] = scan[serial_wiconstants.COUNT_LOW]
        witilt_dict['count_high'] = scan[serial_wiconstants.COUNT_HIGH]
        witilt_dict['x_low'] = scan[serial_wiconstants.X_LOW]
        witilt_dict['x_high'] = scan[serial_wiconstants.X_HIGH]
        witilt_dict['y_low'] = scan[serial_wiconstants.X_LOW]
        witilt_dict['y_high'] = scan[serial_wiconstants.X_HIGH]
        witilt_dict['z_low'] = scan[serial_wiconstants.X_LOW]
        witilt_dict['z_high'] = scan[serial_wiconstants.X_HIGH]
        witilt_dict['r_low'] = scan[serial_wiconstants.R_LOW]
        witilt_dict['r_high'] = scan[serial_wiconstants.R_HIGH]
        #witilt_dict['batt_low'] = scan[serial_wiconstants.BATT_LOW]
        #witilt_dict['batt_high'] = scan[serial_wiconstants.BATT_HIGH]
        return witilt_dict

if __name__ == '__main__':
    witilt = Serial_Connect()