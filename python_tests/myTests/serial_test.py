__author__ = 'chet'
import serial
import gumtools as gt
import time
import sys

def serial_test(port):
    #open serial 1
    serial_one=serial.Serial(port='COM7', baudrate=115200, timeout=1)
    #login
    login = gt.login(serial_one)
    if not login:
        gt.fail([serial_one])
    #open serial 4
    serial_two=serial.Serial(port='COM9', baudrate=115200, timeout=1)
    #start serial test
    serial_one.write('tests/gumstix_serial_test.sh %s\r' % port)
    #1234 written from ser 1
    gt.expect(serial_one, ['1234'], 10)
    #expect 1234 echoed on ser 2
    read = gt.expect(serial_two, ['1234'], 10)
    #wait for ser 1 to listen
    gt.expect(serial_one, ['cat'], 10)
    serial_two.write('4321\r')
    #expect 4321 echoed on ser 1
    write = gt.expect(serial_one, ['4321'], 10)
    #end the test with ctrl-c
    serial_one.write('\x03')
    gt.expect(serial_one, ['[#]'], 5)
    #close the ports when done
    serial_one.close()
    serial_two.close()
    if read == 0 and write == 0:
        print 'PASSED'
    else:
        print 'FAILED'