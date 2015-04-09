#dependencies="00a"
__author__ = 'chet'
#
# $Id$
#
import gumtools as gt
import serial

ser = serial.Serial(port="COM7", baudrate=115200, timeout=1)
if not gt.login(ser):
    gt.fail(ser)
ser.write('tests/gumstix_power_test.sh\r')
gt.expect(ser, ['[#]'], 180)
ser.write('reboot')
#FILL IN TEST HERE
ser.close()
print 'PASSED'
