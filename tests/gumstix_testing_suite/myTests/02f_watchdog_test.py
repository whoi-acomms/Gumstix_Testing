#dependencies="00a"
__author__ = 'chet'
import gumtools as gt
import serial

#open the port and login
ser = serial.Serial(port='COM7', baudrate=115200, timeout=1)
if not gt.login(ser):
    gt.fail(ser)
#find/replace the watchdog file using sed
ser.write("sed -i 's/run_watchdog=1/run_watchdog=0/g' /etc/default/watchdog\r")
if gt.expect(ser, ['[#]'], 5):
    gt.fail(ser)
#reboot
ser.write('reboot\r')
if not gt.login(ser):
    gt.fail(ser)
#expect it to reboot on its own (wait 10 mins plus the ~2 it'd take to reboot)
if gt.expect(ser, ['login:'], 720):
    print "The board failed to reboot with watchdog disabled."
    gt.fail(ser)
print "Rebooted successfully"
#log in again
if not gt.login(ser):
    gt.fail(ser)
#change watchdog back
ser.write("sed -i 's/run_watchdog=0/run_watchdog=1/g' /etc/default/watchdog\r")
if gt.expect(ser, ['[#]'], 5):
    gt.fail(ser)
#reboot
ser.write('reboot\r')
#log in again
if not gt.login(ser):
    gt.fail(ser)
#expect no reboot for 12 mins
if not gt.expect(ser, ['login:'], 720):
    print "The board rebooted despite watchdog being re-enabled."
    gt.fail(ser)
ser.close()
print 'PASSED'