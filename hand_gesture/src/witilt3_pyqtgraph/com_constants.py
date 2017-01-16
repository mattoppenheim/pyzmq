'''
Created on 14 Sep 2015
Constants used for serial port and pydispatcher communications

@author: matthew
'''
BAUD = 115200
# how many samples to store
NUM_SAMPLES = 300
SIGNAL_FROM_GUI_TO_SERIAL = 'signal_from_gui_to_serial'
SIGNAL_FROM_GUI_FOR_DATA = 'signal_from_gui_for_data'
SENDER_FROM_GUI = 'sender_from_gui'
SENDER_FROM_SERIAL = 'sender_from_serial'
SERIAL_PORT = '/dev/ttyUSB0'
SIGNAL_FROM_BOARD = 'signal_from_board'

G_MAX = 3
G_MIN = -3
R_MAX = 3
R_MIN = -3