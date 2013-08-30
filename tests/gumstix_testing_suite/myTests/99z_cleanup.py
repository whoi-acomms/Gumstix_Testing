#dependencies="00a"
__author__ = 'chet'
import gumtools as gt
import serial

ser = serial.Serial(port="COM7", baudrate=115200, timeout=1)
if not gt.login(ser):
    gt.fail(ser)
#write all commented lines to a temp file
ser.write("sed -n '/#/p' /etc/udev/rules.d/70-persistent-net.rules > /etc/udev/rules.d/tmp\r")
if gt.expect(ser, ['[#]'], 10):
    gt.fail(ser)
#mv the temp file to the original
ser.write('mv /etc/udev/rules.d/tmp /etc/udev/rules.d/70-persistent-net.rules\r')
if gt.expect(ser, ['[#]'], 5):
    gt.fail(ser)
ser.write("find /etc/udev/rules.d/ -type f -not -name '70-persistent-net.rules' | xargs rm\r")
if gt.expect(ser, ['[#]'], 5):
    gt.fail(ser)
ser.close()
print 'PASSED'