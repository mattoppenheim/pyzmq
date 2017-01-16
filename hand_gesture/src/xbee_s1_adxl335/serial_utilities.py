'''
Created on 16 May 2016

@author: matthew

serial port utilities
'''
import fnmatch
import os
import xbee_s1_adxl335.utilities as utilities
import serial

def find_pyboard():
    ''' returns the port that the pyboard is connected to '''
        # look for simulated data on /tmp/ttyV1
    ttymodems=fnmatch.filter(os.listdir('/tmp'), 'tty*')
    if ttymodems:
        pyboard_port = '/tmp/'+ ttymodems[1]
        print('*** using simulated data')
        print('socat port is {}'.format(pyboard_port))
        return(pyboard_port)

    # look for a pyboard connected to a /dev/ttyUSB<n> port (XBee port)
    ttymodems = fnmatch.filter(os.listdir('/dev'), 'ttyUSB*')
    pyboard_port = False
    if ttymodems:
        pyboard_port = '/dev/' + ttymodems[0]
        print('found XBee connection at {}'.format(pyboard_port))
        return(pyboard_port)
    # look for a pyboard connected to a /dev/ttyACM<n> port (wire port)
    ttymodems = fnmatch.filter(os.listdir('/dev'), 'ttyACM*')
    pyboard_port = False
    if ttymodems:
        pyboard_port = '/dev/' + ttymodems[0]
        print('found wire connection at {}'.format(pyboard_port))
        return(pyboard_port)

    if not pyboard_port:
        return None

        
def serial_connect(serial_port, baud):
    ''' Return a serial port connection. '''
    print('Trying to connect to serial port: {}'.format(serial_port))
    try:
        serial_connection = serial.Serial(serial_port, baud, rtscts=True,dsrdtr=True)
        serial_connection.flushInput()
    except serial.SerialException as e:
        print('serial_connect error {}'.format(e))
        print('Could not open serial port, try\nsocat -d -d pty,raw,echo=0,link=/tmp/ttyV0 pty,raw,echo=0,link=/tmp/ttyV1')
        return None
    print('Serial port {} set up with baud {}'.format(serial_port, baud))
    return serial_connection

def write(message, serial_connection):
    ''' write data over serial port '''
    serial_connection.write(message)
    serial_connection.flush()
