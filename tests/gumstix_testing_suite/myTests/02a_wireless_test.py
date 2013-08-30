#dependencies="00a"
__author__ = 'chet'

import gumtools as gt
import serial
import sys

ser = serial.Serial(port='COM7', baudrate=115200, timeout=1)
login = gt.login(ser)
if not login:
    gt.fail(ser)
ser.write('iwlist scanning\r')
wireless = gt.expect(ser, ['acommsnet', 'Atlantic', 'WHOI_Meeting', 'Arctic'], 10)
gt.expect(ser, ['[#]'], 10)
if wireless == -1:
    gt.fail(ser)
ser.close()
print 'PASSED'