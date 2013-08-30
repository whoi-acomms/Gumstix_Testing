#dependencies="00a,02e"
#This test requires a usb cable connecting USB OTG to USB host on the testbox and a mounted USB card in the board 2nd slot
#as well as the 'gumstix_usb_test.sh' bash script on the board
__author__ = 'chet'
import gumtools as gt
import serial

#open the port and login
ser = serial.Serial(port="COM7", baudrate=115200, timeout=1)
if not gt.login(ser):
    gt.fail(ser)
#run the usb test and check the output
ser.write('tests/gumstix_usb_test.sh\r')
usbtest = gt.expect(ser, ['PASSED', 'FAILED'], 20)
#report accordingly
if usbtest == -1:
    print 'An unanticipated error occurred while testing the USB connection, please reseat the SD card,' \
          ' check all cables and reboot the board.'
    gt.fail(ser)
elif usbtest == 1:
    print 'Writing a ~1MB file over USB host/OTG connection failed, please reseat the SD card,' \
          ' check all cables and reboot the board.'
    gt.fail(ser)
else:
    ser.close()
    print 'PASSED'