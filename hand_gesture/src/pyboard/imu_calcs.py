'''
Created on 3 Apr 2016

@author: matthew
calculations for IMU data, e.g. IMU6050
pitch, roll

http://stackoverflow.com/questions/3755059/3d-accelerometer-calculate-the-orientation
Roll = atan2(Y, Z) * 180/M_PI;
Pitch = atan2(-X, sqrt(Y*Y + Z*Z)) * 180/M_PI;
to compensate for gimbal lock:
Roll  = atan2( Y,   sign* sqrt(Z*Z+ miu*X*X));
sign  = 1 if accZ>0, -1 otherwise 
miu = 0.001
'''

MIU = 0.001

import numpy as np

def get_pitch(x,y,z):
    ''' Uses accelerometer values to return IMU pitch. '''
    pitch = np.arctan2(-x, np.sqrt(y**2 + z**2)) *180/np.pi
#     if z>0:
#         sign = 1
#     else:
#         sign = -1
#     pitch = np.arctan2(x, sign*np.sqrt(MIU*y**2 + z**2)) *180/np.pi

    return pitch

def get_roll(x,y,z):
    ''' Uses accelerometer values to return IMU roll. '''
    if z>0:
        sign = 1
    else:
        sign = -1
    roll = np.arctan2(y,sign*np.sqrt(z**2+MIU*x**2))*180/np.pi
    return roll


