'''
Created on 2 July 2015

@author: matthew
witilt3 gui using tk
Uses dispatcher to send signals from the tk ggui to the witilt_connect thread
to be sent to the witilt board.
Disabling the battery increased sampling from 120Hz to 143Hz. Disabling the gyro as well gets 160Hz.

'''
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
import tkinter as tk
from tkinter import Tk, Frame, Label, StringVar, LEFT, RIGHT, BOTH, RAISED


from witilt3 import serial_wiconstants
from collections import deque

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
# number samples to plot
SAMPLES = 300
# max/min gravity and degrees per second to plot
G_MAX = 3
G_MIN = -3
R_MAX = 3
R_MIN = -3

LARGE_FONT= ("Verdana", 12)
f = Figure(figsize=(10,5), dpi=100)
a = f.add_subplot(111)


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

class WitiltTk(Frame):

    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.counter = 1
        self.timer = get_time()
        self.x_stringvar = StringVar()
        self.y_stringvar = StringVar()
        self.z_stringvar = StringVar()
        self.r_stringvar = StringVar()
        self.x_deque = deque()
        self.counter_deque = deque()


        self.messages_label = StringVar()
        dispatcher.connect(self.dispatch_from_board, signal=SIGNAL_FROM_BOARD, sender=dispatcher.Any)
        witilt_thread = threading.Thread(target=self.start_witilt)
        witilt_thread.start()
        self.initUI()

    def animate(self, i):
        ''' Animate matplotlib graph with sensor data. '''
        #print('x_deque, y_deque {} \n {}'.format(self.x_deque, self.y_deque))
        a.clear()
        a.set_ylim([-1,1])
        a.plot(self.counter_deque, self.x_deque)


    def initUI(self):
        ''' Set up the user interface. '''
        self.parent.title('Witilt data')
        frame = Frame(self, relief=RAISED, borderwidth=1)
        frame.pack(fill=BOTH, expand=1)
        self.pack(fill=BOTH, expand=1)
        canvas = FigureCanvasTkAgg(f, self)
        canvas.show()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        message_label = Label(self, text = 'witilt data')
        message_label.pack()
        x_label = Label(self, text = 'x_acc', textvariable = self.x_stringvar, bg="red", fg="white")
        y_label = Label(self, text = 'y_acc', textvariable = self.y_stringvar, bg="green", fg="black")
        z_label = Label(self, text = 'z_acc', textvariable = self.z_stringvar, bg="blue", fg="white")
        r_label = Label(self, text = 'r_acc', textvariable = self.r_stringvar, bg="yellow", fg="black")
        x_label.pack(side=LEFT)
        y_label.pack(side=LEFT)
        z_label.pack(side=LEFT)
        r_label.pack(side=LEFT)

    def button_send_press(self, user_input):
        print('button send to witilt pressed')
        if user_input:
            print('textinput: {}'.format(user_input))
        self.send_socket(user_input)



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

    def update_witilt_values(self, board_data):
        ''' Update witilt sensor values in gui. '''
        #print('updating x: {}'.format(board_data['x_acc']))
        x_gravity = self.raw_to_g(board_data['x_acc'], serial_wiconstants.X_MID, serial_wiconstants.X_WIDTH)
        y_gravity = self.raw_to_g(board_data['y_acc'], serial_wiconstants.Y_MID, serial_wiconstants.Y_WIDTH)
        z_gravity = self.raw_to_g(board_data['z_acc'], serial_wiconstants.Z_MID, serial_wiconstants.Z_WIDTH)
        r_gyro  = self.raw_to_gyro(board_data['r_deg'], serial_wiconstants.R_ZERO)
        self.x_stringvar.set('{:1.3f}'.format(x_gravity))
        self.y_stringvar.set('{:1.3f}'.format(y_gravity))
        self.z_stringvar.set('{:1.3f}'.format(z_gravity))
        self.r_stringvar.set('{:2.3f}'.format(r_gyro))
        self.x_deque.append(x_gravity)
        self.counter_deque.append(board_data['count'])
        if len(self.x_deque) > SAMPLES:
            self.x_deque.popleft()
            self.counter_deque.popleft()
            #print('x_deque {}\ncounter_deque {}'.format(self.x_deque, self.counter_deque))

        #self.update_graph((x_gravity, y_gravity, z_gravity, r_gyro))
        # measure update frequency
        if (board_data['count_low'] == 0xff):
            interval = (get_time()-self.timer).total_seconds()
            message = '0xff scans, interval {:1.3f}s, sample freq {:2.3f} Hz'.format(interval, 0xff/interval)
            print(message)
            self.messages_label.set(message)
            self.timer = get_time()

    def send_socket(self, message_txt):
        ''' use dispatcher to send a message to the bluetooth socket through witilt_connect '''
        dispatcher.send(signal=SIGNAL_FROM_GUI, message=message_txt)
        print('sent message to board: {}'.format(message_txt))

    def start_witilt(self):
        ''' Instigate the witilt communication. '''
        #self.witilt = Bluetooth_Connect()
        self.witilt = Serial_Connect()
#         try:
#             self.witilt = Serial_Connect()
#         except Exception as e:
#             print('Unable to connect with witilt, error: {}'.format(e))

if __name__=='__main__':
    app = Tk()
    WitiltTk = WitiltTk(app)

    ani = animation.FuncAnimation(f, WitiltTk.animate, interval=150)
    app.mainloop()
    #app = WitiltTk()
    #ani = animation.FuncAnimation(f, animate, interval = 1)
    #app.mainloop()