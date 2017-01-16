Reads data from the witilt3 from Sparkfun, no longer manufactured. The witilt has 2 modes of data
transfer - bluetooth and serial. I created different classes for bluetooth or serial interface.
I tried pygtk, but it couldn't keep up with the data rate for update. Kivy could, but the
graphing is limited so I finally tried tk and matplotlib with animation.

Get the board streaming using coolterm or gtkterm.
serial_connect.py connects via an ftdi cable.
bluetooth_connect.py connects via bluetooth.
witilt_kivy.py has the kivy gui.
tk_witilt.py has the tk gui.

The gui classes instantiate a serial or bluetooth_connect class, this is set in code.
The _connect classes can be run on their own and print data to the console.
The _connect and witilt_ files communicate using dispatchers.

Matthew Oppenheim July 2015


