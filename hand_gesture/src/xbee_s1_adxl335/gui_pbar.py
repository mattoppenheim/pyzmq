'''
Created on 27 Apr 2016

@author: matthew oppenheim

use a progress bar to represent acceleration value
two progress bars for an accelerometer - one negative

'''

import pyqtgraph as pg
from PySide import QtGui

class Gui_Pbar():
    def __init__(self, title='', color='', max=2):
        ''' max value = max '''
        self.layout_pbar = pg.LayoutWidget()
        #self.layout_pbar.setSpacing(0)
        self.pos_pbar = QtGui.QProgressBar()
        self.neg_pbar = QtGui.QProgressBar()
        self.neg_pbar.setInvertedAppearance(True)
        #self.pbar.setTextVisible(False)
        self.title = title
        self.max = max
        self.pos_pbar.setFormat('')
        self.neg_pbar.setFormat('')
        self.pos_pbar.setGeometry(30, 40, 200, 25)
        self.neg_pbar.setGeometry(30, 40, 200, 25)
        if color:
            self.change_color(color)
        self.layout_pbar.addWidget(self.neg_pbar, row=1, col=1)
        self.layout_pbar.addWidget(self.pos_pbar, row=1, col=2)
        
    def change_color(self, color):
        ''' change the progress bar color '''
        template_css = """QProgressBar::chunk { background: %s; }"""
        css = template_css % color
        self.pos_pbar.setStyleSheet(css)
        self.neg_pbar.setStyleSheet(css)
        
    def change_text(self, text):
        ''' display text on progress bar '''
        self.pos_pbar.setFormat(text)
        
    def return_pbar(self):
        return self.layout_pbar
    
    def update_pbar(self, acc_value):
        ''' Set the value of the pbar. '''
        value = acc_value*100/self.max
        if acc_value>0:
            self.neg_pbar.setValue(0)
            self.pos_pbar.setValue(value)
            self.change_text('{} {:0.2f}'.format(self.title, acc_value))
        else:
            self.pos_pbar.setValue(0)
            self.neg_pbar.setValue(-value)
            self.change_text('{} {:0.2f}'.format(self.title, acc_value))
        
        