'''
GUI component to show real time accelerometer data as a 3D vector_plot

Created on 16 Feb 2016

@author: matthew
'''

import pyboard.accelerometer_data_structure as ads
import numpy as np
import pyqtgraph as pg
import pyqtgraph.opengl as gl
TRAIL_LENGTH = 10

class Gui_Vector:
    def __init__(self):
        self.plot_3d = gl.GLViewWidget()
        self.plot_3d.opts['distance'] = 20
        self.vector_plot = gl.GLLinePlotItem()
        self.trail = np.array(ads.initialise_array(rows=TRAIL_LENGTH, cols = 3))
        self.trail_plot = gl.GLLinePlotItem()
        self.plot_vector([2,3,4])
        self.plot_3d.addItem(self.vector_plot)
        self.plot_3d.addItem(self.trail_plot)
        self.draw_axis(self.plot_3d)

    def add_point_to_trail(self, point):
        ''' add latest Point3D from sensor to the end of the trail '''
        self.trail[:-1] = self.trail[1:]
        self.trail[-1] = point

    def draw_axis(self,plot):
        ''' draw x,y,z axis on to plot '''
        yellow = pg.glColor(255,255,0)
        green = pg.glColor(0,255,0)
        blue = pg.glColor(0,0,255)
        x_axis = gl.GLLinePlotItem(pos=np.array(([-3,0,0],[3,0,0])),color=yellow, width=5)
        y_axis = gl.GLLinePlotItem(pos=np.array(([0,-3,0],[0,3,0])),color=green, width=5)
        z_axis = gl.GLLinePlotItem(pos=np.array(([0,0,-3],[0,0,3])),color=blue, width=5)
        plot.addItem(x_axis)
        plot.addItem(y_axis)
        plot.addItem(z_axis)

    def plot_vector(self, end_point):
        ''' plot vector_plot from origin to end_point '''
        line_pos = np.array(([0,0,0],end_point))
        self.vector_plot.setData(pos=line_pos,
            color=pg.glColor((255,165,0)), width=5)

    def plot_trail(self, point):
        ''' plot trail '''
        self.add_point_to_trail(point)
        self.trail_plot.setData(pos=self.trail, color=pg.glColor((255,165,0)), width=5)

    def return_plot(self):
        return self.plot_3d

