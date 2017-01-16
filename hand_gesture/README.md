Display accelerometer data read from an ADXL335 using an XBee Series 1.

Based on code which communicates with a pyboard. The pyboard reads data from an accelerometer. 

In this case, there is no pyboard. The XBee reads the accelerometer using its ADC.

The accelerometer data structure is detailed in accelerometer_data_structure. With the pyboard, a start and end marker is added in the pyboard code 'ST' and 'EN'. These are not present with the XBee data.
An extra column of absolute acceleration data is added compared with the earlier pyboard iteration.
