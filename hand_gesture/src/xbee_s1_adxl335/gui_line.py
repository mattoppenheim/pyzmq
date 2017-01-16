'''
Created on 29 Apr 2016

@author: matthew oppenheim
line graphs using pyqtgraph
use GraphicsLayoutWidget so that plots can be superimposed
'''

from xbee_s1_adxl335 import accelerometer_data_structure as ads
import pyqtgraph as pg
import numpy as np

class Gui_Line():
    def __init__(self):
        self.layout = pg.GraphicsLayoutWidget()
        self.x_acc_plot = self.layout.addPlot(title='x_acceleration')
        self.x_acc_plot.setYRange(-ads.AMPLITUDE,ads.AMPLITUDE)
        self.layout.nextRow()
        self.y_acc_plot = self.layout.addPlot(title='y_acceleration')
        self.y_acc_plot.setYRange(-ads.AMPLITUDE,ads.AMPLITUDE)
        self.layout.nextRow()
        self.z_acc_plot = self.layout.addPlot(title='z_acceleration')
        self.z_acc_plot.setYRange(-ads.AMPLITUDE,ads.AMPLITUDE)
        self.layout.nextRow()
        self.abs_acc_plot = self.layout.addPlot(title='abs_acceleration')
        self.abs_acc_plot.setYRange(0,2.5*ads.AMPLITUDE)
        
    def return_lines(self):
        return self.layout
    
    def update_x(self, x_data):
        self.x_acc_plot.clear()
        pen=pg.mkPen('r', width=2)
        self.x_acc_plot.plot(x_data, pen=pen)
    
    def update_y(self, y_data):
        self.y_acc_plot.clear()
        pen = pg.mkPen('g', width=2)
        self.y_acc_plot.plot(y_data, pen=pen)
        
    def update_z(self, z_data):
        self.z_acc_plot.clear()
        pen = pg.mkPen('b', width=2)
        self.z_acc_plot.plot(z_data, pen=pen)
        
    def update_abs_acc(self, abs_data, gesture_x, gesture_y):
        self.abs_acc_plot.clear()
        pen = pg.mkPen('y', width=2)
        self.abs_acc_plot.plot(abs_data,pen=pen)
        self.abs_acc_plot.plot(gesture_x, gesture_y, symbol='o', pen=None)
        
        
    