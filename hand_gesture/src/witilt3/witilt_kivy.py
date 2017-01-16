'''
Created on 15 Jun 2015

@author: matthew
witilt3 gui using kivy
Uses dispatcher to send signals from the kivy gui to the witilt_connect thread
to be sent to the witilt board.
Disabling the battery increased sampling from 120Hz to 143Hz. Disabling the gyro as well gets 160Hz.

'''
import kivy
import string
import serial_wiconstants
import sys
kivy.require('1.7.0')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty, NumericProperty
from kivy.garden.graph import Graph, MeshLinePlot
# bluetooth_connect used if using a bluetooth connection
# serial_connect used for wired connection
from bluetooth_connect import Bluetooth_Connect
from serial_connect import Serial_Connect
import threading
from pydispatch import dispatcher
import time
from time import strftime
from  datetime import datetime
from pydispatch import dispatcher
SIGNAL_FROM_GUI = 'signal_from_gui'
SIGNAL_FROM_BOARD = 'signal_from_board'
NUM_SAMPLES = 300
G_MAX = 3
G_MIN = -3
R_MAX = 3
R_MIN = -3

Builder.load_file('witilt_kivy.kv')

def exit_code(message):
    print (message)
    print ("End program")
    sys.exit() # end cleanly

def now_time():
    '''Returns the local time as a string.'''
    now = datetime.now()
    return now.strftime("%H:%M:%S.%f")

def get_time():
    ''' Returns the local time as a datetime. '''
    return datetime.now()

class MyBoxLayout(BoxLayout):
    text_input = ObjectProperty(None)

    def __init__(self):
        super(MyBoxLayout, self).__init__()
        self.counter = 1
        self.messages_label.text = 'top'
        self.timer = get_time()
        self.start_graph()
        dispatcher.connect(self.dispatch_from_board, signal=SIGNAL_FROM_BOARD, sender=dispatcher.Any)
        witilt_thread = threading.Thread(target=self.start_witilt)
        witilt_thread.start()

    def button_send_press(self, user_input):
        print('button send to witilt pressed')
        if user_input:
            print('textinput: {}'.format(user_input))
        self.send_socket(user_input)

    def button2_press(self, instance):
        print('button 2 pressed')
        self.label1_text = 'button2 pressed'

    def dispatch_from_board(self, board_data):
        ''' Handle dispatches from the board to the gui. '''
        #print('received dispatch from board: {}'.format(message))
        out_str = ''
        board_data['x_acc'] = board_data['x_high']*256 + board_data['x_low']
        board_data['y_acc'] = board_data['y_high']*256 + board_data['y_low']
        board_data['z_acc'] = board_data['z_high']*256 + board_data['z_low']
        board_data['r_deg'] = board_data['r_high']*256 + board_data['r_low']
        #board_data['batt'] = board_data['batt_high']*256 + board_data['batt_low']
        board_data['count'] = board_data['count_high']*256 + board_data['count_low']
#         for key, value in sorted(board_data.items()):
#             out_str += '{}:{:02x} '.format(key, value)
        #print('{}: {}'.format(now_time(), out_str))
        self.update_witilt_values(board_data)

    def raw_to_g(self, raw_data, midpoint, width):
        ''' Convert raw accelerometer data to g. '''
        g =  (raw_data - midpoint)/width
        if g > G_MAX:
            print('G_MAX exceeded {:0.3f}'.format(g))
            g = G_MAX
        if g < G_MIN:
            print('G_MIN exceeded {:0.3f}'.format(g))
            g = G_MIN
        return g

    def raw_to_gyro(self, raw_data, zero):
        ''' Convert raw gyro data to degrees per second. '''
        r = (raw_data - zero)/341
        if r > R_MAX:
            print('R_MAX exceeded {:0.3f}'.format(r))
            r = R_MAX
        if r < R_MIN:
            print('R_MIN exceeded {:0.3f}'.format(r))
            r = R_MIN
        return r

    def reset_plots(self, plots):
        ''' Zero all the plots <plots>. '''
        for plot in plots:
            plot.points = [(0,0)]

    def start_graph(self):
        ''' Set up the accelerometer data graph. '''
        #self.acc_graph.xlabel = 'x axis'
        self.plot = []
        self.plot.append(MeshLinePlot(color=[1, 0, 0, 1])) # x - red
        self.plot.append(MeshLinePlot(color=[0, 1, 0, 1])) # y - green
        self.plot.append(MeshLinePlot(color=[0, 0, 1, 1])) # z - blue
        self.plot.append(MeshLinePlot(color=[1 ,1, 1, 1])) # r - white
        self.reset_plots(self.plot)
        for plot in self.plot:
            self.acc_graph.add_plot(plot)

    def update_graph(self, xyz_data):
        ''' Update the graph with new xyzr data. '''
        if self.counter == NUM_SAMPLES:
            for plot in self.plot:
                del(plot.points[0])
                plot.points[:] = [(i[0]-1, i[1]) for i in plot.points[:]]
            self.counter = NUM_SAMPLES-1
        self.plot[0].points.append((self.counter, xyz_data[0]))
        self.plot[1].points.append((self.counter, xyz_data[1]))
        self.plot[2].points.append((self.counter, xyz_data[2]))
        self.plot[3].points.append((self.counter, xyz_data[3]))
        self.counter += 1

    def update_witilt_values(self, board_data):
        ''' Update witilt sensor values in gui. '''
        #print('updating x: {}'.format(board_data['x_acc']))
        x_gravity = self.raw_to_g(board_data['x_acc'], serial_wiconstants.X_MID, serial_wiconstants.X_WIDTH)
        y_gravity = self.raw_to_g(board_data['y_acc'], serial_wiconstants.Y_MID, serial_wiconstants.Y_WIDTH)
        z_gravity = self.raw_to_g(board_data['z_acc'], serial_wiconstants.Z_MID, serial_wiconstants.Z_WIDTH)
        r_gyro  = self.raw_to_gyro(board_data['r_deg'], serial_wiconstants.R_ZERO)
        self.x_label.text = '{:1.3f}'.format(x_gravity)
        self.y_label.text = '{:1.3f}'.format(y_gravity)
        self.z_label.text = '{:1.3f}'.format(z_gravity)
        self.r_label.text = '{:2.3f}'.format(r_gyro)

        self.update_graph((x_gravity, y_gravity, z_gravity, r_gyro))
        # measure update frequency
        if (board_data['count_low'] == 0xff):
            interval = (get_time()-self.timer).total_seconds()
            message = '0xff scans, interval {:1.3f}s, sample freq {:2.3f} Hz'.format(interval, 0xff/interval)
            print(message)
            self.messages_label.text = message
            self.timer = get_time()

    def send_socket(self, message_txt):
        ''' use dispatcher to send a message to the bluetooth socket through witilt_connect '''
        dispatcher.send(signal=SIGNAL_FROM_GUI, message=message_txt)
        print('sent message to board: {}'.format(message_txt))

    def start_witilt(self):
        ''' Instigate the witilt communication. '''
        #self.witilt = Bluetooth_Connect()
        try:
            self.witilt = Serial_Connect()
        except Exception as e:
            print('Unable to connect with witilt, error: {}'.format(e))

class WitiltKivy(App):
    def build(self):
        return MyBoxLayout()

if __name__=='__main__':
    WitiltKivy().run()