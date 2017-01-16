'''
Created on 29 Apr 2016

@author: matthew oppenheim
line graphs using pyqtgraph
'''

import pyboard.accelerometer_data_structure as ads
import pyqtgraph as pg
import numpy as np

class Gui_Line():
    def __init__(self):
        self.plot_x_acc = pg.PlotWidget(title="x accelerometer")
        self.plot_y_acc = pg.PlotWidget(title="y accelerometer")
        self.plot_z_acc = pg.PlotWidget(title="z accelerometer")
#                self.curve_y_acc.setPen(color=(0,255,0),width=2) # green
#         

        self.plot_x_acc.setYRange(-ads.AMPLITUDE,ads.AMPLITUDE)
        self.plot_y_acc.setYRange(-ads.AMPLITUDE,ads.AMPLITUDE)
        self.plot_z_acc.setYRange(-ads.AMPLITUDE,ads.AMPLITUDE)
        self.plot_x_acc.setLabel('left', 'amplitude', units='')
        self.plot_x_acc.setLabel('bottom', 'sample', units='')
        self.curve_x_acc = self.plot_x_acc.plot()
        self.curve_y_acc = self.plot_y_acc.plot()
        self.curve_z_acc = self.plot_z_acc.plot()
        self.curve_z_acc.setPen(color=(0,0,255),width=2) # blue
        self.layout_lines = pg.LayoutWidget()
        self.layout_lines.addWidget(self.plot_x_acc, row=1, col=1)
        self.layout_lines.addWidget(self.plot_y_acc, row=2, col=1)
        self.layout_lines.addWidget(self.plot_z_acc, row=3, col=1)
        
    def return_lines(self):
        return self.layout_lines
        
        
    