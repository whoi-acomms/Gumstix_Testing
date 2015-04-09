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

ser.write('tests/alsa_setup.sh\r')
gt.expect(ser, ['[#]'], 5)
ser.write('tests/gumstix_audio_test.sh\r')
gt.expect(ser, ['[#]'], 15)
ser.close()
print 'PASSED'
