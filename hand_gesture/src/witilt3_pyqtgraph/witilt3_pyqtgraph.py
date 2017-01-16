'''
Created on 20 Aug 2015

@author: matthew
gui using pyqtgraph
Uses dispatcher to send signals from the pyqtgraph gui to the witilt_connect thread
to be sent to the witilt board.
Initial design is for a Sparkfun witilt3 using serial over the debug port using an FTDI cable
Class design is to enable the witilt3 to be replaced by any inertial board.
Add device specific files to replace witilt3_device and witilt3_constants.
Change line 'self.sensor_board = Witilt3_Device()' in serial_connect.
'''

## Enable fault handling to give more helpful error messages on crash.
## Only available in python 3.3+
try:
    import faulthandler
    faulthandler.enable()
except ImportError:
    pass

import PySide
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
from pyqtgraph.ptime import time
import sys
import resources

NUM_SAMPLES = 300
FREQ_AVG = 100
# for a 60Hz monitor use 60
SCREEN_REFRESH_RATE = 50

class witilt3_pyqtgraph():
    def __init__(self):
        self.app = QtGui.QApplication([])
        x_acc = self.initialise_data()
        y_acc = self.initialise_data()
        z_acc = self.initialise_data()
        self.acc_data = [x_acc, y_acc, z_acc]
        self.initialise_data()
        win = pg.GraphicsWindow()
        win.setWindowTitle('pyqtgraph real time data test')
        p1 = win.addPlot()
        win.nextRow()
        p2 = win.addPlot()
        win.nextRow()
        p3 = win.addPlot()
        for plot in [p1, p2, p3]:
            plot.setYRange(-3,3)
        # color=(255,255,0) is yellow
        self.text = pg.TextItem('test text', anchor=(0,3))
        p1.addItem(self.text)

        self.curve1 = p1.plot()
        self.curve2 = p2.plot()
        self.curve3 = p3.plot()
        self.index = 0
        self.last_time = time()
        self.freq = None
        self.freq_list = np.zeros(FREQ_AVG)

    def initialise_data(self):
        ''' Create a numpy arrays of 0s. '''
        return np.zeros(NUM_SAMPLES,dtype=float)

    def roll_data(self, data):
        ''' rolls <data> by one sample'''
        # using slices is 2.5 times faster than using np.roll
        data[:-1] = data[1:]
        return data

    def update(self):
        ''' update the plot curves with a new value'''
        now_time = time()
        dt = now_time - self.last_time
        self.last_time = now_time
        if self.freq is None:
            self.freq = 1.0/dt
        else:
            s = np.clip(dt*3., 0, 1)
            self.freq = self.freq * (1-s) + (1.0/dt) * s
        self.freq_list[-1] = self.freq
        for data in self.acc_data:
            data[-1] = np.random.normal()
        self.text.setText('self.frequency: {:0.1f}'.format(FREQ_AVG*np.average(self.freq_list), color=(255,255,0)))
        self.curve1.setData(self.acc_data[0])
        self.curve2.setData(self.acc_data[1])
        self.curve3.setData(self.acc_data[2])
        for data in self.acc_data:
            data = self.roll_data(data)
        else:
            self.index+=1
        self.app.processEvents()

if __name__ == '__main__':
    import sys
    graph = witilt3_pyqtgraph()
    timer = QtCore.QTimer()
    timer.timeout.connect(graph.update)
    # timer units are milliseconds. timer.start(0) to go as fast as practical.
    timer.start(1000/SCREEN_REFRESH_RATE)
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_'):
        QtGui.QApplication.instance().exec_()
