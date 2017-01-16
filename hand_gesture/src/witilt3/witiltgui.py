'''
Created on 10 Jun 2015

@author: matthew oppenheim
GUI for witilt interaction. GTK3 using glade.
Found that the label updates would die. Moved to kivy and tk.
'''
from gi.repository import Gtk, GLib
# BlueScan sets up the link with the witilt board
from blue_scan import BlueScan
import threading
from pydispatch import dispatcher
import time
from time import strftime
from  datetime import datetime

SIGNAL = 'dispatch'

class WitiltGui(Gtk.Window):
    ''' Create the witilt GUI. '''
    def __init__(self):
        print('WitiltGui instantiated')
        # set up dispatcher to enable communication with witilt board
        dispatcher.connect(self.handle_dispatcher, signal=SIGNAL, sender=dispatcher.Any)
        gladefile = 'witiltgui.glade'
        builder = Gtk.Builder()
        builder.add_from_file(gladefile)
        window = builder.get_object('main_window')
        GLib.threads_init()

        self.message_label1 = builder.get_object('message_label1')
        self.x_data_label = builder.get_object('x_data_label')
        self.y_data_label = builder.get_object('y_data_label')
        builder.connect_signals(self)
        self.write_message_label1('WiTiltGui')
        window.show_all()
        self.main()

    def main(self):
        ''' Start the gtk drawing the gui and responding to events. '''
        witilt_thread = threading.Thread(target=self.start_witilt)
        #thread.daemon = True
        witilt_thread.start()
        check_thread = threading.Thread(target=self.periodic_check(self))
        check_thread.start()

        #run Gtk.main() last
        Gtk.main()

    def handle_dispatcher(self, message):
        ''' pydispatch event handler '''
        message=message.__str__()
        print('dispatch {}'.format(message))
        #self.write_message_label1(message)
        self.write_message_label1('dispatcher')

    def message_button1_clicked(self, button):
        ''' Handle button1 click event. '''
        print('message_button1_clicked')
        self.write_message_label1('message_button1_clicked')

    def message_button2_clicked(self, button):
        ''' Handle button2 click event. '''
        print('message_button2_clicked')
        self.write_message_label1('message_button2_clicked')

    def now_time(self):
        '''returns the local time as a string'''
        now = datetime.now()
        return now.strftime("%H:%M:%S")

    def periodic_check (self, gui):
        ''' update message label1 periodically '''
        print('periodic_check started')
        while True:
            time.sleep(1)
            gui.write_message_label1(self.now_time())
            print('periodic_check')



    def start_witilt(self):
        ''' Instigate the witilt communication. '''
        self.witilt = BlueScan(self)


    def write_message_label1(self, text):
        ''' Display text on message_label1. '''
        #print('received text {}'.format(text))
        self.message_label1.set_text(text)

    def write_x_data_label(self, text):
        ''' Display text on x_data_label. '''
        self.x_data_label.set_text(text)



if __name__ == '__main__':
    win = WitiltGui()





