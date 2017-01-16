'''
GUI component to display status data
Created on 26 Apr 2016

@author: matthew
'''

import pyqtgraph as pg
import pyboard.accelerometer_data_structure as ads
from PySide import QtCore, QtGui
import math

class Gui_Status():
    def __init__(self):
        self.status_layout = pg.LayoutWidget()
        self.graph_freq_text = QtGui.QLabel('fps: {}'.format(ads.FRAMES_PER_SECOND))
        self.sensor_sample_rate_text = QtGui.QLabel('sample rate: {}'.format(ads.FRAMES_PER_SECOND))
        self.acc_amp_text = QtGui.QLabel(('total acceleration:'))
        self.status_layout.addWidget(self.acc_amp_text,row=4,col=1)
        self.status_layout.addWidget(self.graph_freq_text, row=5, col=1)
        self.status_layout.addWidget(self.sensor_sample_rate_text, row=6, col=1)
        
    def return_plot(self):
        return self.status_layout
    
    def update_acceleration(self, x, y, z):
        ''' Set x,y,z values. '''
        acc_amp = math.sqrt(x**2 + y**2 + z**2)
        self.acc_amp_text.setText('total acceleration: {:0.2f}'.format(acc_amp))
