'''
Created on 3 Jul 2015

@author: matthew
To display witilt data. Called in a thread from witilt_vispy.
'''

import itertools
import numpy as np
import time
from time import strftime
from  datetime import datetime
from vispy import app, scene
from vispy.color import get_colormaps
from vispy.visuals.transforms import STTransform
from vispy.ext.six import next
from pydispatch import dispatcher
from collections import deque
import serial_wiconstants

SIGNAL_FROM_GUI = 'signal_from_gui'
SIGNAL_FROM_BOARD = 'signal_from_board'
# number samples to plot
SAMPLES = 400
# max/min gravity and degrees per second to plot
G_MAX = 3
G_MIN = -3
R_MAX = 3
R_MIN = -3

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

class VispyGraph():


    def __init__(self):
        dispatcher.connect(self.vispy_dispatch_from_board, signal=SIGNAL_FROM_BOARD, sender=dispatcher.Any)
        # vertex positions of data to draw
        self.pos = np.zeros((SAMPLES, 2), dtype=np.float32)
        #self.pos[:, 0] = np.linspace(10, 390, SAMPLES)
        #self.pos[:, 1] = np.random.normal(size=SAMPLES, scale=20, loc=0)
        self.x = deque(range(1,SAMPLES+1))
        self.y = deque(np.zeros(SAMPLES))
        self.pos[:, 0] = self.x
        self.pos[:, 1] = self.y

        canvas = scene.SceneCanvas(keys='interactive', size=(400, 200), show=True)

        # Create a visual that updates the line with different colormaps
        self.line = scene.Line(pos=self.pos, color='y', method='gl')
        self.line.transform = STTransform(translate=[0, 140])
        self.line.parent = canvas.central_widget

        timer = app.Timer('auto', connect=self.on_timer, start=True)

        canvas.app.run()

    def vispy_dispatch_from_board(self, board_data):
        ''' Handle dispatches from the board to the gui. '''
        out_str = ''
        board_data['x_acc'] = board_data['x_high']*256 + board_data['x_low']
        board_data['y_acc'] = board_data['y_high']*256 + board_data['y_low']
        board_data['z_acc'] = board_data['z_high']*256 + board_data['z_low']
        board_data['r_deg'] = board_data['r_high']*256 + board_data['r_low']
        #board_data['batt'] = board_data['batt_high']*256 + board_data['batt_low']
        board_data['count'] = board_data['count_high']*256 + board_data['count_low']
#         for key, value in sorted(board_data.items()):
#             out_str += '{}:{:02x} '.format(key, value)
#         print('{}: {}'.format(now_time(), out_str))
        self.update_witilt_values(board_data)

    def update_witilt_values(self, board_data):
        ''' Update witilt sensor values in gui. '''
        x_gravity = self.raw_to_g(board_data['x_acc'], serial_wiconstants.X_MID, serial_wiconstants.X_WIDTH)
        y_gravity = self.raw_to_g(board_data['y_acc'], serial_wiconstants.Y_MID, serial_wiconstants.Y_WIDTH)
        z_gravity = self.raw_to_g(board_data['z_acc'], serial_wiconstants.Z_MID, serial_wiconstants.Z_WIDTH)
        r_gyro  = self.raw_to_gyro(board_data['r_deg'], serial_wiconstants.R_ZERO)
        self.y.append(50*x_gravity)
        if len(self.y) > SAMPLES:
            self.y.popleft()

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


    def on_timer(self, event):
        self.pos[:, 0] = self.x
        self.pos[:, 1] = self.y
        self.line.set_data(pos=self.pos, color='y')
        #print('x {}\ny {}'.format(self.x, self.y))

if __name__ == '__main__':
    VispyGraph = VispyGraph()
