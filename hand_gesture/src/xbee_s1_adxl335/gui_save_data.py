'''
Created on 3 May 2016

@author: matthew oppenheim
based on the ZetCode Pyside tutorial
Handles creating and writing data to a file.

'''
import pyboard.accelerometer_data_structure as ads
import numpy as np
import os
import sys
from pydispatch import dispatcher
import pyqtgraph as pg
from PySide import QtGui

class Gui_SaveData(QtGui.QWidget):
    
    def __init__(self):
        super(Gui_SaveData, self).__init__()
        self.overwrite = False
        self.save_data = False
        self.replay_data = False
        self.main()
        
    def main(self):
        self.data_layout = pg.LayoutWidget()
        self.output_filepath = '/home/matthew/data/documents/infolab2/projects/hand_gesture/gui_data/data.txt'
        self.output_file = self.open_file(self.output_filepath)
        self.save_loc_button = QtGui.QPushButton("save/replay file location")
        self.save_loc_button.setToolTip('Select where to save your data to or replay from')
        self.save_loc_button.clicked.connect(self.save_loc_button_handler)
        self.message_label = QtGui.QLabel()
        self.update_message_label()
        self.overwrite_button = QtGui.QPushButton("overwrite/append")
        self.overwrite_button.setCheckable(True)
        self.overwrite_button.clicked[bool].connect(self.overwrite_button_handler)
        self.save_data_buton = QtGui.QPushButton('save data')
        self.save_data_buton.clicked.connect(self.save_data_button_handler)
        self.setGeometry(200, 200, 200, 100)
        self.data_layout.addWidget(self.save_loc_button,row=1,col=1)
        self.data_layout.addWidget(self.overwrite_button,row=2,col=1)
        self.data_layout.addWidget(self.message_label,row=3,col=1)
        self.data_layout.addWidget(self.save_data_buton,row=4,col=1) 
        
    def close_file(self, file_object):
        ''' close file_path '''
        file_object.close()
        
    def dispatcher_send_port(self):
        ''' send out that the replay port should be used, or not '''
        if self.replay_data:
            message_txt = 'replay_port'
        else:
            message_txt = 'not_replay_port'
        print('dispatching: {}'.format(message_txt))
        dispatcher.send(signal=ads.PORT_SIGNAL, message=message_txt, sender=ads.PORT_SENDER)
         
    def get_output_file(self):
        ''' return the output file object '''
        return self.output_file
    
    def get_layout(self):
        ''' returns the layout '''
        return self.data_layout
      
    def initialise_file(self, file_path):
        ''' create a blank file '''
        if os.path.exists(file_path):
            print('over writing {}'.format(file_path))
        file_object = open(file_path,'w')
        file_object.close()
        
    def make_visible(self):
        self.show()
        
    def open_file(self, file_path):
        ''' returns a file object '''
        if self.overwrite:
            file_object = open(file_path, 'wb')
        else:
            file_object = open(file_path, 'ab')
        return file_object
    
    def overwrite_button_handler(self):
        ''' toggles overwrite and append for files '''
        self.overwrite = not(self.overwrite)
        self.update_message_label()
    
    def replay_button_handler(self):
        ''' replay saved sensor data '''
        self.replay_data = not(self.replay_data)
        self.dispatcher_send_port()
        self.update_message_label()
    
    def save_data_button_handler(self):
        self.save_data = not self.save_data
        if not self.save_data:
            try:
                self.close_file(self.output_file)
            except Exception as e:
                print('could not close file {}\n{}'.format(self.output_filepath, e))
        if self.save_data:
            try:
                self.output_file = self.open_file(self.output_filepath)
            except Exception as e:
                print('could not open file{}\n{}'.format(self.output_filepath,e))
        self.update_message_label()
            
    def save_loc_button_handler(self):
        ''' brings up a file location widget '''
        fname, _ = QtGui.QFileDialog.getOpenFileName(self, 'Open file',
            '/home')
        if fname:
            try:
                self.close(self.output_file)
            except TypeError as e:
                print('new file')
            self.output_filepath = fname
            self.output_file = self.open_file(self.output_filepath)
        self.update_message_label()
        
    def unique_rows(self, np_a, np_b):
        ''' return rows in numpy array b that are not also in numpy array a) '''
        alist = [tuple(x) for x in np_a]
        blist = [tuple(x) for x in np_b]
        return np.array([x for x in blist if x not in alist])
        
    def update_message_label(self):
        self.message_label.setText(
            'output file: {}\noverwrite: {}\nlogging data: {}\nreplay data from file: {}'.format(
            self.output_filepath, self.overwrite, self.save_data, self.replay_data))                                                                                             
                                                                                                    
    def write_to_file(self, data):
        ''' write <data> to the output file '''
        self.output_file.write(data.__str__())
        self.output_file.write('\n') # new line
        
    def write_numpy_array_to_file(self, new_np_array, old_np_array):
        ''' write numpy array to file after removing overlapping data from old_np_array'''
        new_data = self.unique_rows(old_np_array, new_np_array)
        np.set_printoptions(threshold=np.nan)
        # if sample rate < update rate, then the new_data will be empty
        if new_data.size == 0:
            return
        #print(new_data)
        try:
            np.savetxt(self.output_file, new_data, fmt='%d %d %f %f %f %f')
        except ValueError as e:
            print('{}\n{}'.format(e, new_data))
        
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    save_data = Gui_SaveData()
    save_data.make_visible()
    sys.exit(app.exec_())