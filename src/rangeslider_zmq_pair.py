'''
Created on 10 Oct 2016

@author: matthew oppenheim
use pyzmq pair context for communication
set up rangesliders and slider to describe filter parameters
for peak detection algorithm used in shake gesture recognition
send the parameters using zmq to the detection process e.g. xbee_s1_adxl335
'''
from datetime import datetime
from gesture_dict import GestureDict
import logging
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QTimer
from PyQt4.QtGui import QSlider
from qrangeslider import QRangeSlider
import sys
import zmq
from zmq.eventloop import zmqstream
from _datetime import date

FRAMES_PER_SECOND = 5

class RangesliderZmq(QtGui.QWidget):
    
    def __init__(self):
        #app = QtGui.QApplication(sys.argv)
        super().__init__()
        self.gesture_dict = GestureDict()
        self.port = 5556
        logging.basicConfig(level=logging.DEBUG, format='%(message)s')
        self.initUI()
        #sys.exit(app.exec_())
        
    def initUI(self):
        port = self.port
        self.create_socket(port)
        range_label = QtGui.QLabel('events')
        self.range_events = QRangeSlider()   
        self.range_events.show()
        self.range_events.setFixedWidth(300)
        self.range_events.setFixedHeight(36)
        self.range_events.setMin(0)
        self.range_events.setMax(4)
        self.range_events.setRange(0,1)
        self.range_events.startValueChanged.connect(lambda: self.keep_slider_min(self.range_events))
        hbox_events = QtGui.QHBoxLayout()
        hbox_events.addWidget(range_label)
        hbox_events.addWidget(self.range_events)
        self.textbox = QtGui.QLineEdit()
        self.update_btn = QtGui.QPushButton("update")
        self.update_btn.clicked.connect(lambda: self.button_click(port))
        self.update_btn.setFixedWidth(100)
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.update_btn)

        magnitude_label = QtGui.QLabel('magnitude in g/10')
        self.range_magnitude = QRangeSlider() 
        self.range_magnitude.show()    
        self.range_magnitude.setFixedWidth(300)
        self.range_magnitude.setFixedHeight(36)
        self.range_magnitude.setMin(20)
        self.range_magnitude.setMax(80)
        self.range_magnitude.setRange(20, 30)
 
        hbox_magnitude = QtGui.QHBoxLayout()
        hbox_magnitude.addWidget(magnitude_label)
        hbox_magnitude.addWidget(self.range_magnitude)
        self.filter_length = QRangeSlider()
        self.filter_length.show() 
        self.filter_length.setFixedWidth(300)
        self.filter_length.setFixedHeight(36)
        self.filter_length.setMin(0)
        self.filter_length.setMax(250)
        self.filter_length.setRange(0,100)
        self.filter_length.startValueChanged.connect(lambda: self.keep_slider_min(self.filter_length))
        filter_length_label = QtGui.QLabel('filter length in samples')
        hbox_length = QtGui.QHBoxLayout()
        hbox_length.addWidget(filter_length_label)
        hbox_length.addWidget(self.filter_length)
        self.message_label = QtGui.QLabel("messages will be here")
        self.exit_btn = QtGui.QPushButton('exit')
        self.exit_btn.clicked.connect(lambda: self.exit_click(self.socket, self.context, port)) 
        vbox = QtGui.QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(hbox_events)
        vbox.addLayout(hbox_magnitude)
        vbox.addLayout(hbox_length)
        vbox.addWidget(self.message_label)
        vbox.addWidget(self.update_btn)
        vbox.addLayout(hbox)
        vbox.addWidget(self.exit_btn)
        self.setLayout(vbox)    
        self.setGeometry(300, 300, 300, 150)
        self.setWindowTitle('rangesliders')
        self.show()
     
    @QtCore.pyqtSlot()   
    def button_click(self, port):
        ''' handle button click event '''
        try:
            self.update_gesture_dict()
            message = self.gesture_dict.make_json()
            logging.info('rangeslider sending message {}'.format(message))
            self.socket.send_json(message, flags=zmq.NOBLOCK)
        except zmq.error.Again as e:
            logging.info('no receiver for the message: {}'.format(e))
            # restart the socket if nothing to receive the message
            # if receiver closed, the socket needs to be restarted
            self.close_socket()
            self.create_socket(port)
            
    def close_socket(self):
        ''' close the socket and context '''
        self.socket.close()
        self.context.term()

    def create_socket(self, port):
        ''' create a socket using pyzmq with PAIR context '''
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PAIR)
        self.socket.setsockopt(zmq.LINGER, 0 )
        self.socket.bind("tcp://*:%s" % port)
        stream_pair = zmqstream.ZMQStream(self.socket)
        stream_pair.on_recv(self.process_message)

    def exit_click(self, socket, context, port):
        ''' handle exit button click '''
        socket.close()
        context.term()
        sys.exit() 
        
    def filter_length_change(self):
        ''' filter length slider has changed '''
        length = self.filter_length.value()
        self.set_message_label('filter_length: {}'.format(length))
        
    def keep_slider_min(self, slider):
        ''' keep the slider length minimum as one '''
        try:
            slider.setStart(0)
        except RuntimeError as e:
            pass
        self.set_message_label('cannot change this')

    def process_message(self, msg):
        time = datetime.now()
        time = time.strftime('%H:%M:%S')
        text = ('{}: {}'.format(time,msg))
        self.message_label.setText(text) 
        
    def set_message_label(self, text):
        self.message_label.setText(text)
        
    def timer_timeout(self):
        ''' handle the QTimer timeout '''
        try:
            msg = self.socket.recv(flags=zmq.NOBLOCK).decode()
            self.process_message(msg)
        except zmq.error.Again as e:
            return
        
    def update_gesture_dict(self):
        ''' get status of all the rangesliders into GestureDict object '''
        magnitude_min, magnitude_max = self.range_magnitude.getRange()
        filter_length = self.filter_length.end()
        events = self.range_events.end()
        self.gesture_dict.update_dict(magnitude_min=magnitude_min, \
            magnitude_max=magnitude_max/10, events=events, \
            filter_length=filter_length)
                
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    ex = RangesliderZmq()
    #app.setQuitOnLastWindowClosed(False)
    timer = QTimer()
    timer.timeout.connect(ex.timer_timeout)
    timer.start(1000/FRAMES_PER_SECOND)
    app.exec_() 
