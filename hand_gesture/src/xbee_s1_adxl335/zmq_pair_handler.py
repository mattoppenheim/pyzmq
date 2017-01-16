'''
pyzmq pair socket handler
Created on 1 Nov 2016
using qt timer and polling instead of the tornado loop in zmq
@author: matthew oppenheim
'''

import xbee_s1_adxl335.accelerometer_data_structure as ads
import json
import logging
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
import zmq
import sys
import time

class ZmqPair():
    def __init__(self):
        logging.basicConfig(level=logging.DEBUG, format='%(message)s')
        port = '5556'
        self.socket, context = self.create_socket(port)
        
    def create_socket(self, port):
        ''' return the zmq.PAIR socket and context  '''
        context = zmq.Context()
        socket = context.socket(zmq.PAIR)
        socket.connect('tcp://localhost:%s' % ads.ZMQ_PORT) 
        socket.setsockopt(zmq.LINGER, 0)
        return socket, context
    
    def send_message(self, text):
        ''' send message to socket '''
        self.socket.send_string(text)
        logging.info('sent {} to socket'.format(text))
        
    def get_message(self):
        ''' get json message through socket and return '''
        msg = None
        try:
            msg = self.socket.recv(flags=zmq.NOBLOCK).decode()
            self.send_message('received message')
            return json.loads(msg)
        # raises zmq.errror.Again if no message
        except zmq.error.Again as e:
            pass
 