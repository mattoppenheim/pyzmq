'''
Created on 10 Oct 2016

@author: matthew oppenheim
use pyzmq pair context for communication
'''
from datetime import datetime
from gesture_dict import GestureDict
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QTimer
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
        self.initUI()
        #sys.exit(app.exec_())
        
    def initUI(self):
        port = self.port
        self.create_socket(port)
        range_label = QtGui.QLabel('duration')
        self.range_duration = QRangeSlider()   
        self.range_duration.show()
        self.range_duration.setFixedWidth(300)
        self.range_duration.setFixedHeight(36)
        self.range_duration.setMin(0)
        self.range_duration.setMax(1000)
        self.range_duration.setRange(200,800)
        hbox_duration = QtGui.QHBoxLayout()
        hbox_duration.addWidget(range_label)
        hbox_duration.addWidget(self.range_duration)
        self.textbox = QtGui.QLineEdit()
        self.update_btn = QtGui.QPushButton("update")
        self.update_btn.clicked.connect(lambda: self.button_click(port))
        self.update_btn.setFixedWidth(100)
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.update_btn)
        pitch_label = QtGui.QLabel('pitch')
        self.range_pitch = QRangeSlider()    
        self.range_pitch.show()    
        self.range_pitch.setFixedWidth(300)
        self.range_pitch.setFixedHeight(36)
        self.range_pitch.setMin(-80)
        self.range_pitch.setMax(80)
        self.range_pitch.setRange(-20, 20)
        hbox_pitch = QtGui.QHBoxLayout()
        hbox_pitch.addWidget(pitch_label)
        hbox_pitch.addWidget(self.range_pitch)
        roll_label = QtGui.QLabel('roll')
        self.range_roll = QRangeSlider()    
        self.range_roll.show()    
        self.range_roll.setFixedWidth(300)
        self.range_roll.setFixedHeight(36)
        self.range_roll.setMin(-80)
        self.range_roll.setMax(80)
        self.range_roll.setRange(-20, 20)
        hbox_roll = QtGui.QHBoxLayout()
        hbox_roll.addWidget(roll_label)
        hbox_roll.addWidget(self.range_roll)
        self.message_label = QtGui.QLabel("messages will be here")
        self.exit_btn = QtGui.QPushButton('exit')
        self.exit_btn.clicked.connect(lambda: self.exit_click(self.socket, self.context, port)) 
        vbox = QtGui.QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(hbox_pitch)
        vbox.addLayout(hbox_roll)
        vbox.addLayout(hbox_duration)
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
            self.socket.send_json(message, flags=zmq.NOBLOCK)
        except zmq.error.Again as e:
            print('no receiver for the message: {}'.format(e))
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

    def process_message(self, msg):
        time = datetime.now()
        time = time.strftime('%H:%M:%S')
        text = ('{}: {}'.format(time,msg))
        self.message_label.setText(text) 
        
    def set_message_label(self, text):
        self.message_label.setText(text)
        
    def timer_timeout(self):
        ''' handle the QTimer timeout '''
        #print('timer_timout')
        try:
            msg = self.socket.recv(flags=zmq.NOBLOCK).decode()
            self.process_message(msg)
        except zmq.error.Again as e:
            return
        
    def update_gesture_dict(self):
        ''' get status of all the rangesliders into GestureDict object '''
        pitch_min, pitch_max = self.range_pitch.getRange()
        roll_min, roll_max = self.range_roll.getRange()
        duration_min, duration_max = self.range_duration.getRange()
        self.gesture_dict.update_dict(pitch_min=pitch_min, pitch_max=pitch_max, \
            roll_min=roll_min, roll_max=roll_max, duration_min=duration_min, \
            duration_max=duration_max)
                
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    ex = RangesliderZmq()
    #app.setQuitOnLastWindowClosed(False)
    timer = QTimer()
    timer.timeout.connect(ex.timer_timeout)
    timer.start(1000/FRAMES_PER_SECOND)
    app.exec_() 
