'''
Created on 5 Jun 2015

@author: matthew
find and connect with a Sparkfun witilt using bluetooth

if there is failure to connect, make the owner of rfcomm0 the user that runs this script ***
e.g. sudo chown matther /dev/rfcomm0

splits the socket data into chunks of length LENGTH_SCAN - change this if sensors are disabled
Send '1' to get witilt menu
Send 'S' to start binary data collection
Send 'A' to abort binary data collection

'''

# Butchered code from http://people.csail.mit.edu/albert/bluez-intro/x232.html
# Pairs the witilt with the PC

import bluetooth
import sys
from time import strftime
from  datetime import datetime
import bluetooth_wiconstants
from pydispatch import dispatcher
from time import sleep
SIGNAL_FROM_GUI = 'signal_from_gui'
SIGNAL_FROM_BOARD = 'signal_from_board'
#witilt scan has 15 bytes with start byte, x,y,z accelerometer, gyro, battery and count bytes
LENGTH_SCAN = 15
TRIMMED = 2

#from WitiltGui import WitiltGui

#PORT = 0x1001 # from example code for L2CAP
PORT = 1# RFCOMM
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

class Bluetooth_Connect():
    ''' Creates a bluetooth connection with a WiTilt. '''
    witilt_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    WITILT_ADD = '00:06:66:01:F1:A2' # address of target witilt
    #WITILT_ADD = '00:06:66:00:DF:ED' # address of target witilt
    WITILT_NAME = 'FireFly-F1A2' # name of target witilt

    def __init__(self):
        print("{} Looking for Bluetooth devices...".format(now_time()))
        # set up dispatcher to enable communication with witilt board
        dispatcher.connect(self.dispatch_from_gui, signal=SIGNAL_FROM_GUI, sender=dispatcher.Any)
        self.last_count_low = 0
        self.previous_widata = bytes()
        bt_sock = self.connect(self.WITILT_ADD, self.witilt_sock)
        self.get_data(bt_sock)

    def bytes_to_hex(self, byte_data):
        ''' returns all the bytes in byte_data as byte code, not the character.'''
        output = ''
        for char in byte_data:
            output += ('{:02x} '.format(char))
        return output

    def dispatch_from_gui(self, message):
        ''' Pydispatch event handler for incoming signals. Sends message to socket. '''
        self.send_socket(message.__str__())

    def periodic_display(self, data):
        ''' Periodically update display. This approach doesn't work. Move to WitiltGui. '''
        time_now = datetime.now()
        time_delta = time_now-self.datetime
        if time_delta.total_seconds() > UPDATE_FREQ:
            self.datetime = time_now
            print(now_time())
            #self.write_message_witiltgui('t: {}'.format(time_now))
            dispatcher.send(signal=SIGNAL_FROM_BOARD, message='t: {}'.format(now_time()))

    def process_widata(self, widata):
        ''' Parse and display a complete witilt data scan. '''
        #print('widata {} len: {}'.format(self.bytes_to_hex(widata), len(widata)))
        # if no data, return
        if not widata:
            return
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
            print('{}: {}'.format(now_time(), self.bytes_to_hex(scan)))
            #if not scan.startswith(start_byte):
                #print('--- {} wrong start byte for {} scans: {} widata: {}'.format(now_time(), scan, scans, widata))
            if not scan.endswith(end_byte):
                print('+++ {} wrong end byte for {} scans: {} widata: {}'.format(now_time(), scan, scans, widata))
                continue
            # We have trimmed off the '#@' bytes from the start of the scan
            if len(scan) != LENGTH_SCAN-TRIMMED:
                print('*** {} incorrect length {} for {} scans: {} widata: {}'.format(now_time(), len(scan), scan, scans, widata))
                continue
            self.count_high = scan[bluetooth_wiconstants.COUNT_HIGH]
            self.count_low = scan[bluetooth_wiconstants.COUNT_LOW]
            self.x_low = scan[bluetooth_wiconstants.X_LOW]
            self.x_high = scan[bluetooth_wiconstants.X_HIGH]
            # 0x0a (new line symbol) not used in low_count location, skips from 0x09 to 0x0b
            if self.count_low - self.last_count_low not in (1, -255) and self.count_low != (0x0b):
                print('### missing {} scans'.format(str(self.count_low - self.last_count_low-1)))
                print(self.previous_widata)
                print(widata)
            self.last_count_low = self.count_low
#
#             print('count_high {:02x} count_low {:02x} y_high {:02x} y_low {:02x}'
#                    .format(self.count_high, self.count_low, self.x_high, self.x_low))
            #self.periodic_display(self.count_low)
            #dispatcher.send(signal=SIGNAL_FROM_BOARD, message=('count_low={}'.format(self.count_low)))
        self.previous_widata = widata

    def send_socket(self, text):
        ''' Send text to bluetooth socket. '''
        print('sending {} to socket'.format(text))
        self.witilt_sock.send(text)

    def connect(self, WITILT_ADD, sock):
        ''' Connect to the witilt using a socket. '''
        try: # try to scan for bluetooth devices
            nearby_devices = bluetooth.discover_devices(duration=5,lookup_names = True, flush_cache=True)
        except IOError as e: # Probably no Bluetooth adapter found
            exit_code('error: {} \n probably no Bluetooth adapter'.format(e))
        print("found %d devices" % len(nearby_devices))
        for addr, name in nearby_devices:
            print("  %s - %s" % (addr, name))
            if addr == WITILT_ADD:
                print("\nFound witilt: {} Trying to connect \n".format(WITILT_ADD))
                sock.connect((WITILT_ADD, PORT))# for RFCOMM a (host,channel) tuple
        return sock


    def get_data(self, sock):
        ''' Get data from the socket. '''
        print('Sending 1, 1, S to start streaming')
        sock.send('1')
        sleep(0.2)
        sock.send('1')
        sleep(0.2)
        sock.send('S')
        sleep(0.2)
        try:
            sock.listen(1)
            # if the witilt is already connected an IOError will be raised
            print('sock.listen(1) run')
        except(IOError):
            print('witilt connected')
        self.send_socket('S')
        print('Asking for data')
        complete_scan = bytes()
        while (1):
            new_data = sock.recv(1024)
            # no data
            if not new_data:
                continue
            # start of incomplete data scan
            if new_data.startswith(start_byte) and len(new_data) < LENGTH_SCAN:
                complete_scan = new_data
                #print('{} short data, appending with next: {}'.format(now_time(), new_data))
                continue
            # data scan, with a beginning and end symbol
            if new_data.startswith(start_byte) and new_data.endswith(end_byte):
                self.process_widata(new_data)
                complete_scan = bytes()
                continue
            # end of an incomplete scan
            if new_data.endswith(end_byte):
                self.process_widata(complete_scan+new_data)
                complete_scan = bytes()
                continue
            # No start or end detected. Probably 'b'#' detected.
            else:
                complete_scan = complete_scan + new_data
                continue
            # for gravity mode, '.decode' removes the b' part and cleans up output
            #print('{} {} data: {}'.format(counter.__str__(), now_time(), new_data.decode()))
            # for gravity and binary mode 'repr' outputs all of the new_data string, including 'b''
            #print('{} {} new_data: {}'.format(counter.__str__(), now_time(), repr(new_data)))



    def return_data(self):
        return self.count_low

if __name__ == '__main__':
    witilt = Bluetooth_Connect()







