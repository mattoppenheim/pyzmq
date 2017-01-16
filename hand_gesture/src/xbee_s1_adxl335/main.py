'''
Created on 31 Dec 2015
graph x,y,z accelerometer data coming from XBee series 1 
@author: matthew
testing git
'''

#import xbee_s1_adxl335.accelerometer_data_structure as ads
#from euclid import Point2,Point3
from xbee_s1_adxl335 import imu_calcs
import logging
import math
from xbee_s1_adxl335 import accelerometer_data_structure as ads
import numpy as np
import PySide
from pydispatch import dispatcher
from pyqtgraph.Qt import QtGui, QtCore
from pyqtgraph.ptime import time
from xbee_s1_adxl335.gesture import Gesture
from xbee_s1_adxl335.gesture_recognition import Gesture_Recognition
from xbee_s1_adxl335.pyboard_connect_wire import Pyboard_Connect_Wire
from xbee_s1_adxl335.pyboard_connect_xbee import Pyboard_Connect_XBee
from xbee_s1_adxl335.xbee_connect import Xbee_Connect
from xbee_s1_adxl335.gui_main import Gui
from xbee_s1_adxl335.replay_data import ReplayData
import sys
import threading
from xbee_s1_adxl335 import utilities
from xbee_s1_adxl335 import serial_utilities
from xbee_s1_adxl335.zmq_pair_handler import ZmqPair
from pyboard import gesture

# display will have limits +/- AMPLITUDE
AMPLITUDE = 2
# for a 60Hz monitor use 60
FRAMES_PER_SECOND = 30
FREQ_AVG_SAMPLES = 200

SAMPLE_RATE = 200

PYBOARD_SIGNAL_HEADERS = 'sensor_signal_headers'

time_list=[]

class Graph_Accelerometer():
    def __init__(self):
        self.create_gui()
        #logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        logging.basicConfig(level=logging.DEBUG, format='%(message)s')
        # set up a dispatcher to receive data from serial_to_dispatch
        self.sensor_data = ads.initialise_array()
        dispatcher.connect(self.dispatcher_receive_acc, signal=ads.SENSOR_SIGNAL_ACC, sender=ads.PYBOARD_SENDER)
        dispatcher.connect(self.dispatcher_receive_headers, signal=PYBOARD_SIGNAL_HEADERS, sender=ads.PYBOARD_SENDER)
        dispatcher.connect(self.dispatcher_receive_gesture, signal=ads.GESTURE_SIGNAL, sender=ads.GESTURE_SENDER)
        dispatcher.connect(self.dispatcher_receive_port, signal=ads.PORT_SIGNAL, sender=ads.PORT_SENDER)
        data_thread = threading.Thread(target=self.start_pyboard)
        data_thread.start()

        #set up for measuring graph refresh frequency
        self.last_time = time()
        self.freq_list = np.zeros(FREQ_AVG_SAMPLES)
        self.freq = None
        self.dispatcher_send('send_headers', signal=ads.DISPLAY_SIGNAL, sender=ads.DISPLAY_SENDER)
        # the gesture that we are trying to match on
        self.gesture = Gesture()
        self.sensor_data = None
        # handles zmq communications with the gesture definition gui
        self.zmq = ZmqPair()
        # gesture_coords saves the coordinates where a gesture is matched in a frame of abs_acc data
        self.gesture_coords = Gesture_Recognition()
        logging.info('instigated main')

    def create_gui(self):
        self.app = QtGui.QApplication([])
        self.win = QtGui.QMainWindow()
        self.win.resize(1000,800)
        self.win.setWindowTitle('real time graph')

        gui = Gui(self.win)
        self.win.setCentralWidget(gui.area)

        self.win.show()
        gui.frequency_button.clicked.connect(self.frequency_button_clicked)
        self.acc_curves = gui.gui_lines
        self.graph_freq_text = gui.gui_status.graph_freq_text
        self.sensor_sample_rate_text = gui.gui_status.sensor_sample_rate_text
        self.frequency_spinbox = gui.frequency_spinbox
        self.log_txtedit = gui.log_txtedit
        self.accel_vector = gui.gui_vector
        self.accel_vector.plot_vector([-2,-3,-1])
        self.roll_arrow = gui.roll_arrow
        self.pitch_arrow = gui.pitch_arrow
        self.pitch_text = gui.pitch_text
        self.roll_text = gui.roll_text
        self.gui_status = gui.gui_status
        self.x_pbar = gui.x_pbar
        self.y_pbar = gui.y_pbar
        self.z_pbar = gui.z_pbar
        self.amp_pbar = gui.amp_pbar
        self.save_data = gui.gui_save_data

    def dispatcher_receive_acc(self, message):
        ''' Deal with np.array accelerometer data received through the dispatcher. '''
        self.old_sensor_data = self.sensor_data
        self.sensor_data = message
        self.x_acc = self.sensor_data[:,2]
        self.y_acc = self.sensor_data[:,3]
        self.z_acc = self.sensor_data[:,4]
        self.abs_acc = self.sensor_data[:,5]
        
    def dispatcher_receive_port(self, message):
        ''' Deal with new port for data to be received on. '''
        logging.info('dispatcher_receive_port: {}'.format(message))
        if message == 'replay_port':
            logging.info('replaying data')
            self.replay_data()
    
    def dispatcher_receive_gesture(self, message):
        ''' Deal with messages from gesture class '''
        # remove the following line once this method is tested
        logging.info('received gesture dispatch {}'.format(message))
        self.log_text(message)

    def dispatcher_receive_headers(self, message):
        ''' Deal with header titles received through the dispatcher. '''
        logging.info('acc_data_headers {}'.format(message))

    def dispatcher_send(self, message_txt, signal, sender):
        ''' Use dispatcher to send message_txt to pyboard '''
        #logging.info('from main: {}'.format(message_txt))
        dispatcher.send(signal=signal, message=message_txt, sender=sender)

    def frequency_button_clicked(self):
        sample_rate = self.frequency_spinbox.value()
        signal_to_pyboard=('sample_rate={}'.format(sample_rate))
        text = ('frequency set to: {}'.format(sample_rate))
        self.log_text(text)
        self.dispatcher_send(signal_to_pyboard, signal=ads.WRITE_PYBOARD, sender=ads.DISPLAY_SENDER)

    def graph_update_rate(self):
        ''' Calculate graph refresh frequency. '''
        now_time = time()
        dt = now_time - self.last_time
        self.last_time = now_time
        if self.freq is None:
            self.freq = 1.0/dt
        else:
            s = np.clip(dt*3., 0, 1)
            self.freq = self.freq * (1-s) + (1.0/dt) * s
        self.freq_list[-1] = self.freq
        return(FREQ_AVG_SAMPLES*np.average(self.freq_list))

    def log_text(self, text):
        ''' write text to the log_txtbox '''
        text = ('{} {}\n'.format(utilities.now_time_simple(), text))
        self.log_txtedit.moveCursor(QtGui.QTextCursor.End)
        self.log_txtedit.insertPlainText(text)
    
    def replay_data(self):
        ''' replay data '''
        self.replay_data = ReplayData(self.save_data.output_filepath)
        self.start_pyboard()

    def sensor_update_rate(self):
        ''' Calculate the accelerometer update rate. '''
        #logging.info(' *** {}'.format(self.sensor_data[-FREQ_AVG_SAMPLES:-1,1]))
        sensor_update_rate = 1000000/np.average(self.sensor_data[-FREQ_AVG_SAMPLES:-1,1])
        return(sensor_update_rate)

    def start_pyboard(self):
        ''' Start a connection with the pyboard and request data headers. '''
        serial_connection = serial_utilities.find_pyboard()
        if not serial_connection:
            utilities.exit_code('*** no pyboard or simulated data found ***')
        if 'ttyUSB' in serial_connection:
            self.pyboard = Xbee_Connect()
            print('connected XBee')
            return
        if 'ttyACM' in serial_connection:
            self.pyboard = Pyboard_Connect_Wire(serial_connection=serial_connection)
            return
        # simulated data from sender_sim or replayed data from replay_data
        if 'tmp' in serial_connection:
            logging.info('starting connection through virtual paired ports')
            self.pyboard = Pyboard_Connect_XBee(serial_connection=serial_connection)
            return

    def timer_timeout(self):
        ''' Triggered by QTimer. Get accelerometer data from xbee_s1_adxl335. '''
#         try:
#             logging.info('requesting new data')
#             message=(self.zmq.get_message())
#         except Exception as e:
#             logging.info(e)
#         if message:
#             self.gesture.update_gesture(message)
        self.dispatcher_send('send_data', signal=ads.DISPLAY_SIGNAL, sender=ads.DISPLAY_SENDER)
        try:
            gesture_x, gesture_y  = self.gesture_coords.check_data(self.abs_acc)
            self.update_2d_acc_plots(gesture_x, gesture_y)
        except AttributeError as e:
            logging.info('no abs_acc data')

        try:
            self.last_x, self.last_y, self.last_z = self.x_acc[-1], self.y_acc[-1], self.z_acc[-1]
        except AttributeError as e:
            logging.info('no data available')
            return
        self.update_3d_vector([self.last_x, self.last_y, self.last_z])
        self.update_graph_freq()
        self.sensor_update_rate()
        self.update_pitch_roll()
        self.update_status_text()
        self.update_pbar()
        if self.save_data.save_data:
            self.write_array_file(self.sensor_data, self.old_sensor_data)


            
    def update_2d_acc_plots(self, gesture_x, gesture_y):
        ''' Update accelerometer graphs with sensor data_data. '''
        try:
            self.acc_curves.update_x(self.x_acc)
            self.acc_curves.update_y(self.y_acc)
            self.acc_curves.update_z(self.z_acc)
            self.acc_curves.update_abs_acc(self.abs_acc,gesture_x,gesture_y)
        except AttributeError as e:
            logging.info(e)
            pass

    def update_3d_vector(self, end_point):
        self.accel_vector.plot_vector(end_point)
        self.accel_vector.plot_trail(end_point)

    def update_graph_freq(self):
        ''' update the frequency measurements on the graphs '''
        self.graph_freq_text.setText(
            'measured graph refresh frequency (Hz): {:0.1f}'.format(self.graph_update_rate(), color=(255,255,0)))
        self.sensor_sample_rate_text.setText(
             'measured sensor sample frequency (Hz): {:0.1f}'.format(self.sensor_update_rate(), color=(255,255,0)))

    def update_pbar(self):
        ''' update the progress bars '''
        self.x_pbar.update_pbar(self.last_x)
        self.y_pbar.update_pbar(self.last_y)
        self.z_pbar.update_pbar(self.last_z)
        self.amp_pbar.update_pbar(math.sqrt(self.last_x**2+self.last_y**2+self.last_z**2))

    def update_pitch_roll(self):
        ''' Update the pitch and roll indicators '''
        self.pitch = imu_calcs.get_pitch(self.last_x,self.last_y,self.last_z)
        self.roll = imu_calcs.get_roll(self.last_x,self.last_y,self.last_z)
        self.pitch_text.setText('pitch: {:0.1f}'.format(self.pitch))
        self.roll_text.setText('roll: {:0.1f}'.format(self.roll))
        self.pitch_arrow.setRotation(self.pitch)
        self.pitch_arrow.setTransformOriginPoint(20,0)
        self.roll_arrow.setRotation(self.roll)
        self.roll_arrow.setTransformOriginPoint(20,0)

    def update_status_text(self):
        self.gui_status.update_acceleration(self.last_x,self.last_y,self.last_z)

    def write_array_file(self, new_np_array, old_np_array):
        ''' write sensor numpy array to file '''
        # need to add new data onto end of old array
        self.save_data.write_numpy_array_to_file(new_np_array, old_np_array)

if __name__ == '__main__' :
    graph = Graph_Accelerometer()
    timer = QtCore.QTimer()
    timer.timeout.connect(graph.timer_timeout)
    # timer units are milliseconds. timer.start(0) to go as fast as practical.
    timer.start(1000/FRAMES_PER_SECOND)
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()