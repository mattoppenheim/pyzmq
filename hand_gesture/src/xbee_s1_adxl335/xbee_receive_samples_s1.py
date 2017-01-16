#! /usr/bin/python

"""
This example continuously reads the serial port and processes IO data
received from a remote XBee.
g = (ADC_count-512)/102.4
"""
from collections import deque
import numpy as np
from xbee import XBee
import serial
import time

PORT = '/dev/ttyUSB0'
BAUD_RATE = 115200 
g = lambda x: (x-512)/102.4
# Open serial port
ser = serial.Serial(PORT, BAUD_RATE)
# Create XBee Series 1 object
xbee = XBee(ser, escaped=True)
sample_deque = deque([None]*100, maxlen=100)
print('created xbee_s1_adxl335 at {} with baud {}'.format(PORT, BAUD_RATE))
print('listening for data...')
dt_old = time.perf_counter() 
# Continuously read and print packets
while True:
    dt_new = time.perf_counter()
    response = xbee.wait_read_frame()
    adc_dict=response['samples'][0]
    delta_millis = (dt_new-dt_old)*1000
    sample_deque.pop()
    sample_deque.appendleft(delta_millis)
#     try:
#         print('{:.2f}'.format(np.mean(sample_deque)))
#     except TypeError:
#         continue
    dt_old = dt_new
#     try:
#         print('{:.2f} {:.2f}'.format(delta_millis, 1000/delta_millis))
#     except ZeroDivisionError as e:
#         continue
    print('{:.2f} {:.2f} {:.2f}'.format(g(adc_dict['adc-0']), g(adc_dict['adc-1']), g(adc_dict['adc-2'])))
ser.close()
