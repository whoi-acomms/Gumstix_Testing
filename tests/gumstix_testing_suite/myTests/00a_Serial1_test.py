#dependencies=""
__author__ = 'chet'
#
# $Id$
#
import serial
import gumtools as gt

#open serial port to Gumstix Serial 1
serial_one=serial.Serial(port='COM7', baudrate=115200, timeout=1)
#log into board
login = gt.login(serial_one)
serial_one.close()
print 'PASSED' if login else 'FAILED'
