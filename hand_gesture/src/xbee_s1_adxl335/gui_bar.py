'''
Created on 26 Apr 2016
GUI bar chart to show acceleration magnitude

@author: matthew
'''

import pyqtgraph as pg
import numpy as np

class Gui_Bar():
    def __init__(self):
        self.bar_plot = pg.PlotWidget()
        x = np.arange(1)
        self.x_bar = pg.BarGraphItem(x=x, height=1, width=0.3, brush='y')
        self.y_bar = pg.BarGraphItem(x=x+0.5, height=1, width=0.3, brush='g')
        self.z_bar = pg.BarGraphItem(x=x+1, height=1, width=0.3, brush='b')
        self.amp_bar = pg.BarGraphItem(x=x+1.5, height=2, width=0.3, brush='r')
        self.z_bar.height = 3
        self.bar_plot.addItem(self.x_bar)
        self.bar_plot.addItem(self.y_bar)
        self.bar_plot.addItem(self.z_bar)
        self.bar_plot.addItem(self.amp_bar)
        
        
    def return_bar(self):
        return self.bar_plot
    
    def update_bar(self, value):
        ''' Update the value of the bar chart. '''
        self.bar.setValue(value)