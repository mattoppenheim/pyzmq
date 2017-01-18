'''
pyqtgraph layout with a pyzmq pair context
for testing pubsub messaging with pyzmq
Created on 14 Oct 2016
using qt timer and polling instead of the tornado loop in zmq
@author: matthew oppenheim
'''

from gesture_dict import GestureDict
import json
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
import zmq
import sys
import time

FRAMES_PER_SECOND = 30

class PyqtgraphPair(QtGui.QWidget):
    def __init__(self):
        super().__init__()
        port = '5556'
        QtGui.QWidget.__init__(self)
        self.socket, context = self.create_socket(port)
        self.layout = QtGui.QVBoxLayout()
        self.setLayout(self.layout)
        self.label = QtGui.QLabel("data will be here")
        self.exit_btn = QtGui.QPushButton('exit')
        self.exit_btn.clicked.connect(lambda: self.exit_click(self.socket, context, port))
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.exit_btn)
        self.gesture_dict = GestureDict()
        
    def create_socket(self, port):
        ''' return the zmq.PAIR socket and context  '''
        context = zmq.Context()
        socket = context.socket(zmq.PAIR)
        socket.connect('tcp://localhost:%s' % port) 
        socket.setsockopt(zmq.LINGER, 0)
        return socket, context
    
    def exit_click(self, socket, context, port):
        ''' handle exit button click '''
        #socket.disconnect('tcp://localhost:%s' % port)
        socket.close()
        context.term()
        sys.exit()
    
    def send_message(self, text):
        ''' send message to socket '''
        self.socket.send_string(text)
        print('sent {} to socket'.format(text))
        
    def set_label(self, text):
        ''' set the label to text '''
        self.label.setText(text)

    def timer_timeout(self):
        ''' handle the QTimer timeout '''
        try:
            msg = self.socket.recv(flags=zmq.NOBLOCK).decode()
            self.set_label(json.loads(msg))
            self.send_message('data received')
            self.update_gesture(msg)
        except zmq.error.Again as e:
            return
        
    def update_gesture(self, json_msg):
        ''' update the gesture_dict from a json object '''
        self.gesture_dict = json.loads(json_msg)
        print(self.gesture_dict)
        
if __name__ == '__main__':
    pg.mkQApp()
    win = PyqtgraphPair()
    win.show()
    win.resize(200,200)
    timer = QtCore.QTimer()
    timer.timeout.connect(win.timer_timeout)
    timer.start(1000/FRAMES_PER_SECOND)
    #win.set_label('hello')
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()