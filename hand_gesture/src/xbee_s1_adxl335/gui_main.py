'''
GUI to show real time accelerometer data
Created on 15 Feb 2016

@author: matthew
'''

from xbee_s1_adxl335.gui_save_data import Gui_SaveData
from xbee_s1_adxl335.gui_vector import Gui_Vector
from xbee_s1_adxl335.gui_status import Gui_Status
from xbee_s1_adxl335.gui_bar import Gui_Bar
from xbee_s1_adxl335.gui_line import Gui_Line
from xbee_s1_adxl335.gui_pbar import Gui_Pbar
import numpy as np
from PySide import QtCore, QtGui
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from pyqtgraph.dockarea import *

AMPLITUDE = 2

SAMPLE_RATE = 100

class Gui:
    def __init__(self, MainWindow):
        # set up docks
        self.area = DockArea()
        dock_attitude = Dock("attitude", size=(400, 100))
        dock_text = Dock("text", size=(400,100))
        dock_lines = Dock("real time data", size=(800,800))
        dock_3d = Dock("3D acceleration vector", size=(300,100))
        dock_status = Dock("status", size=(200,100))
        dock_frequency = Dock("sampling", size=(100,100))
        dock_bar = Dock('bar', size=(200,200))
        dock_files= Dock('files', size=(200,200))
        # place the docks relative to each other
        self.area.addDock(dock_attitude)     
        self.area.addDock(dock_text,'bottom')
        self.area.addDock(dock_lines,'top')
        self.area.addDock(dock_3d, 'bottom', dock_lines)
        self.area.addDock(dock_status,'left', dock_3d)
        self.area.addDock(dock_frequency, 'right', dock_attitude)
        self.area.addDock(dock_bar, 'right', dock_status)
        self.area.addDock(dock_files, 'right', dock_frequency)

        # sample frequency selection
        self.frequency_spinbox = QtGui.QSpinBox()
        self.frequency_spinbox.setRange(1,500)
        self.frequency_spinbox.setValue(SAMPLE_RATE)
        self.frequency_spinbox.setSingleStep(10)
        self.frequency_button = QtGui.QPushButton('set sensor sample rate')
        frequency_lbl = QtGui.QLabel("sensor sample rate(Hz):")
        layout_frequency = pg.LayoutWidget()
        layout_frequency.addWidget(frequency_lbl, row=1, col=1)
        layout_frequency.addWidget(self.frequency_spinbox, row=2, col=1)
        layout_frequency.addWidget(self.frequency_button, row=3, col=1)
        dock_frequency.addWidget(layout_frequency)
        
        # pitch and roll arrows
        self.pitch_text = pg.TextItem()
        self.roll_text = pg.TextItem()
        self.pitch_arrow = pg.ArrowItem(angle= 180, tipAngle=30, baseAngle=20, \
                                       headLen=40, tailLen=None, brush='g', pos=(0,0))
        self.roll_arrow = pg.ArrowItem(angle= 180, tipAngle=30, baseAngle=20, \
                                       headLen=40, tailLen=None, brush='r', pos=(0,0))
        pitch_arrow_plot = pg.PlotWidget()
        pitch_arrow_plot.addItem(self.pitch_arrow)
        pitch_arrow_plot.addItem(self.pitch_text)
        pitch_arrow_plot.setXRange(-1,1)
        pitch_arrow_plot.setYRange(-1,1)
        roll_arrow_plot = pg.PlotWidget()
        roll_arrow_plot.addItem(self.roll_arrow)
        roll_arrow_plot.addItem(self.roll_text)
        roll_arrow_plot.setXRange(-1,1)
        roll_arrow_plot.setYRange(-1,1)
        layout_attitude = pg.LayoutWidget()
        layout_attitude.addWidget(pitch_arrow_plot, row=1, col=1)
        layout_attitude.addWidget(roll_arrow_plot, row=1, col=2)
        dock_attitude.addWidget(layout_attitude)
        
        # bar graphs
        self.x_pbar = Gui_Pbar(title='x_acc:', color='yellow')
        self.y_pbar = Gui_Pbar(title='y_acc:', color='green')
        self.z_pbar = Gui_Pbar(title='z_acc:', color='blue')
        self.amp_pbar = Gui_Pbar(title='amp_acc:', color='red')
        layout_bars = pg.LayoutWidget()
        layout_bars.addWidget(self.x_pbar.return_pbar(), row=1, col=1)
        layout_bars.addWidget(self.y_pbar.return_pbar(), row=2, col=1)
        layout_bars.addWidget(self.z_pbar.return_pbar(), row=3, col=1)
        layout_bars.addWidget(self.amp_pbar.return_pbar(), row=4, col=1)
        dock_bar.addWidget(layout_bars)     
       
        # text box
        self.log_txtedit = self.setup_log_output()
        dock_text.addWidget(self.log_txtedit)
        
        # accelerometer line graphs
        self.gui_lines = Gui_Line()
        layout_lines = self.gui_lines.return_lines()
        dock_lines.addWidget(layout_lines)
        
        # 3d vector display
        self.gui_vector = Gui_Vector()
        self.plot_3d = self.gui_vector.return_plot()# gl.GLViewWidget()
        dock_3d.addWidget(self.plot_3d)
        
        # status text
        self.gui_status = Gui_Status()
        self.status_text = self.gui_status.return_plot() # pg.LayoutWidget()
        dock_status.addWidget(self.status_text)
        
        # save data dialog
        self.gui_save_data = Gui_SaveData()
        self.save_data_layout = self.gui_save_data.get_layout()
        dock_files.addWidget(self.save_data_layout)


    def setup_log_output(self):
        ''' returns a QTextEdit to record output on '''
        log_txtedit = QtGui.QTextEdit()
        log_txtedit.setReadOnly(True)
        return log_txtedit