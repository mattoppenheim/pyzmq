'''
Created on 12 Jan 2017
Matches gestures in a numpy array.
Find peaks in numpy array of absolute accelerometer data.
Uses a filter window of size filter_win_size, this controls the gesture length 
plot using pyqtgraph. 
@author: matthew oppenheim
'''
import logging
import numpy as np
from matplotlib import pyplot as plt
from skimage import feature
from scipy.ndimage.filters import maximum_filter
import pyqtgraph as pg

class Gesture_Recognition():
    def __init__(self, filter_win_size=50, peak=3):
        self.FILTER_WIN_SIZE = filter_win_size
        # peak threshold for detection
        self.PEAK = peak

    def check_data(self, input_data):
        ''' returns x and y values for where gesture is matched in input_data '''
        max_data = np.nan_to_num(maximum_filter(input_data, self.FILTER_WIN_SIZE))
        min_data = np.nan_to_num(-maximum_filter(input_data, self.FILTER_WIN_SIZE))
        # select places where we detect maximum but not minimum -> we dont want long plateaus
        peak_mask = np.logical_and(max_data == input_data, min_data != input_data)
        # select peaks where we have enough elevation
        peak_mask = np.logical_and(peak_mask, max_data-min_data>self.PEAK)
        peak_mask = peak_mask * 2 - 1
        # select only the up edges to eliminate multiple maximas in a single peak
        peak_mask = np.correlate(peak_mask, [-1, 1], mode='same') == 2
        max_x_values = np.where(peak_mask)[0]
        max_y_values = [input_data[x] for x in max_x_values]
        #logging.info('g_x {} g_y {}'.format(max_x_values, max_y_values))
        return (max_x_values, max_y_values)