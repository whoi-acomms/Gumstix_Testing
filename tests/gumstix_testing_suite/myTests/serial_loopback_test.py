__author__ = 'chet'

import gumtools as gt
import serial
import time

def serial_loopback(gtport):
    #open serial one and login
    ser1 = serial.Serial(port='COM7', baudrate=115200, timeout=1)
    login = gt.login(ser1)
    if not login:
        gt.fail([ser1])
    #list of baudrates to test
    bauds=[4800, 9600, 19200, 115200, 460800]
    for baud in bauds:
        #run the loopback test on the given port at the current baud
        ser1.write('tests/gumstix_serial_loopback_test.sh %s %i\r' % (gtport, baud))
        #estimate of how long it should take to transfer the ~ 1MB file
        time_est = 1024*1024*10 / baud
        #expect a result within 1.5 times the estimate
        sertest = gt.expect(ser1, ['PASSED', 'FAILED'], time_est*1.5)
        #if any baud fails or doesn't return within 1.5 times the estimate, failed test
        if (sertest == 1) | (sertest == -1):
            print 'failing'
            gt.fail([ser1])
        print 'passed on baudrate: %i' % baud
        time.sleep(.5)
    print 'PASSED'