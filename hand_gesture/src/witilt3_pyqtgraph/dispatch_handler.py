'''
Handles dispatches

Created on 20 Aug 2015

@author: matthew
'''

import resources

def dispatch_from_board(self, board_data):
        ''' Handle dispatches from the board to the gui. '''
        #print('received dispatch from board: {}'.format(message))
        out_str = ''
        board_data['x_acc'] = board_data['x_high']*256 + board_data['x_low']
        board_data['y_acc'] = board_data['y_high']*256 + board_data['y_low']
        board_data['z_acc'] = board_data['z_high']*256 + board_data['z_low']
        board_data['r_deg'] = board_data['r_high']*256 + board_data['r_low']
        #board_data['batt'] = board_data['batt_high']*256 + board_data['batt_low']
        board_data['count'] = board_data['count_high']*256 + board_data['count_low']
#         for key, value in sorted(board_data.items()):
#             out_str += '{}:{:02x} '.format(key, value)
        #print('{}: {}'.format(now_time(), out_str))
        self.update_witilt_values(board_data)

def raw_to_g(self, raw_data, midpoint, width):
    ''' Convert raw accelerometer data to g. '''
    g =  (raw_data - midpoint)/width
    if g > resources.G_MAX:
        print('G_MAX exceeded {:0.3f}'.format(g))
        g = resources.G_MAX
    if g < resources.G_MIN:
        print('G_MIN exceeded {:0.3f}'.format(g))
        g = resources.G_MIN
    return g

def raw_to_gyro(self, raw_data, zero):
    ''' Convert raw gyro data to degrees per second. '''
    r = (raw_data - zero)/341
    if r > resources.R_MAX:
        print('R_MAX exceeded {:0.3f}'.format(r))
        r = resources.R_MAX
    if r < resources.R_MIN:
        print('R_MIN exceeded {:0.3f}'.format(r))
        r = resources.R_MIN
    return r


def send_socket(self, message_txt, dispatcher):
    ''' use dispatcher to send a message to the bluetooth socket through witilt_connect '''
    dispatcher.send(signal=resources.SIGNAL_FROM_GUI, message=message_txt)
    print('sent message to board: {}'.format(message_txt))

