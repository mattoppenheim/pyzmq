'''
Created on 19 Jun 2015

@author: matthew

Connect to the serial port and collect sensor data.
Initial design to find and connect with a Sparkfun witilt using serial over
the debug port using an FTDI cable

if there is failure to connect, make the owner of rfcomm0 the user that runs this script ***
e.g. sudo chown matthew /dev/rfcomm0

see witilt3_device for details of witilt3 data protocol

Create a dictionary sensor_data_dic containing numpy arrays. Each array
contains count, accelerometer or gyro data.
This dictionary is requested by the plotting class using a dispatcher.
'''
import bluetooth
import com_constants
from  datetime import datetime
from pydispatch import dispatcher
import serial
import sys
import numpy as np
from time import sleep, strftime
from witilt3_device import Witilt3_Device

# how long to pause in seconds after sending a character to the serial port
PAUSE = 0.2

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

    def __init__(self):
        print('{} Starting Serial_Connect'.format(now_time()))
        self.serial_connect(com_constants.SERIAL_PORT, com_constants.BAUD)
        # set up dispatcher to receive dispatches from the GUI
        dispatcher.connect(self.dispatch_from_gui_to_serial, signal=com_constants.SIGNAL_FROM_GUI_TO_SERIAL,
                           sender=com_constants.SENDER_FROM_GUI)
        dispatcher.connect(self.dispatch_from_gui_for_data, signal=com_constants.SIGNAL_FROM_GUI_FOR_DATA, sender=com_constants.SENDER_FROM_GUI)
        # Initialise numpy arrays to store count, accelerometer and gyro data in
        self.np_count = self.initialise_data(com_constants.NUM_SAMPLES)
        self.np_x_acc = self.initialise_data(com_constants.NUM_SAMPLES)
        self.np_y_acc = self.initialise_data(com_constants.NUM_SAMPLES)
        self.np_z_acc = self.initialise_data(com_constants.NUM_SAMPLES)
        self.np_gyro = self.initialise_data(com_constants.NUM_SAMPLES)
        # set the sensor board that we are interacting with
        self.sensor_board = Witilt3_Device()
        # this is the dictionary of numpy arrays that is passed to the plotting class
        self.sensor_data_dict = {'count':self.np_count, 'x_acc': self.np_x_acc,
                            'y_acc':self.np_y_acc, 'z_acc':self.np_z_acc, 'gyro':self.np_gyro}
        self.last_count_low = 0
        self.previous_scan = bytes()
        self.serial_write('S')
        self.get_serial()

    def bytes_to_hex(self, byte_data):
        ''' Returns all the bytes in byte_data as byte code, not the character.'''
        output = ''
        for char in byte_data:
            output += ('{:02x} '.format(char))
        return output

    def dispatch_from_gui_to_serial(self, message):
        ''' pydispatch event handler. Sends message to serial port. '''
        self.serial_write(message.__str__())

    def dispatch_from_gui_for_data(self, message):
        ''' pydispatch event handler. Dispatches sensor_data_dict to gui. '''
        self.dispatcher.send(signal=com_constants.SIGNAL_FROM_BOARD,
                             message=self.sensor_data_dict, sender=com_constants.SENDER_FROM_SERIAL)

    def dispatcher_send(self, message, signal, sender):
        ''' Use dispatcher to send message_txt. '''
        dispatcher.send(signal=signal, message=message, sender=sender)

    def get_sensor_data(self, scan):
        ''' Splits up the sensor_device scan data and assigns it to the last
        element of the relevant numpy array. '''
        count = self.sensor_board.get_count(scan)
        x_acc = self.sensor_board.get_x_acc(scan)
        y_acc = self.sensor_board.get_y_acc(scan)
        z_acc = self.sensor_board.get_z_acc(scan)
        gyro = self.sensor_board.get_gyro(scan)
        print('count {:04x}  x_acc {:04x} y_acc {:04x} z_acc {:04x} gyro {:04x}'
                   .format(self.np_count[-1], self.np_x_acc, self.np_y_acc,
                           self.np_z_acc, self.np_gyro))
        # make the last element of the data arrays be from the current scan
        self.roll_data(self.np_count, count)
        self.roll_data(self.np_x_acc, x_acc)
        self.roll_data(self.np_y_acc, y_acc)
        self.roll_data(self.np_z_acc, z_acc)
        self.roll_data(self.np_gyro, gyro)

    def get_serial(self,num_bytes = None):
        '''Returns all data from the open serial port.'''
        while (1):
            inWaiting = self.serial.inWaiting()
            read_bytes = self.serial.read(inWaiting)
            if read_bytes:
                # for debugging
                #print(read_bytes)
                # assemble_scans pieces partial scans together.
                self.process_complete_scans(self.sensor_board.assemble_scans(read_bytes))

    def initialise_data(self, length):
        ''' Create a numpy array of <length> 0s. '''
        return np.zeros(length ,dtype=float)

    def process_complete_scans(self, complete_scans):
        ''' Split up and extract sensor data from the complete scans. '''
        scans = self.sensor_board.split_scan(complete_scans)
        for scan in scans:
            self.current_scan = scan
            # assign the scan elements to the relevant numpy arrays in sensor_data_dict
            self.get_sensor_data(scan)

            # check to see if a scan is missing by checking the last two count_low byte
            # 0x0a (new line symbol) not used in low_count location, skips from 0x09 to 0x0b
            if self.np_count[-2] - self.np_count[-1] not in (1, -255) and self.count_low != (0x0b):
                print('### missing {} scans'.format(str(self.np_count[-2] - self.np_count[-1]-1)))
                print('previous scan {}'.format(self.bytes_to_hex(self.previous_scan)))
                print('current scan {}'.format(self.bytes_to_hex(self.current_scan)))
            self.previous_scan = scan

    def process_scan(self, current_scan):
        ''' Splits the witilt3 data into single scans.
        Calls get_sensor_data with a single scan. '''

        # if no data, return
        if not current_scan:
            return
        # trim off /x00 from start of scan string
        current_scan=self.trim_scan(current_scan)

        # split data into single scan lengths
        # sometimes multiple scans are returned, so split on characters between scans '$#'
        scans = current_scan.split(b'#@')
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
            if len(scan) != self.sensor_board.get_length_scan()-TRIMMED:
                print('*** {} incorrect length {} for {} scans: {} current_scan: {}'.format(now_time(), len(scan), scan, scans, current_scan))
                continue
            # assign the scan elements to the relevant numpy arrays in sensor_data_dict
            self.get_sensor_data(scan)

            # check to see if a scan is missing by checking the last two count_low byte
            # 0x0a (new line symbol) not used in low_count location, skips from 0x09 to 0x0b
            if self.np_count[-2] - self.np_count[-1] not in (1, -255) and self.count_low != (0x0b):
                print('### missing {} scans'.format(str(self.np_count[-2] - self.np_count[-1]-1)))
                print('previous scan {}'.format(self.bytes_to_hex(self.previous_scan)))
                print('current scan {}'.format(self.bytes_to_hex(current_scan)))

    def roll_data(self, data_array, new_element):
        ''' Rolls <data> by one sample then makes <new_element> the last element of <data>.'''
        # using slices is 2.5 times faster than using np.roll
        data_array[:-1] = data_array[1:]
        data_array[-1] = new_element

    def serial_connect(self, serial_port, baud):
        ''' Set up the serial port connection. '''
        print('Trying to connect to serial port: {}'.format(serial_port))
        self.serial = serial.Serial(serial_port, baud)
        self.serial.flushInput()
        print('Serial port {} set up with baud {}'.format(self.serial.name, self.serial.baudrate))

    def serial_write(self,ch=' '):
        ''' Writes a character into the port and waits PAUSE seconds. '''
        self.serial.write(bytes(ch, 'ascii'))
        self.serial.flush()
        print('wrote: {} to board'.format(ch))
        sleep(PAUSE)



if __name__ == '__main__':
    serial_connect = Serial_Connect()