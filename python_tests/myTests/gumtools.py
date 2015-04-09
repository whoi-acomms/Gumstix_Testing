__author__ = 'chet'
#
# $Id$
#
import serial
import re
import time
import sys

#This is inteneded to naively imitate the expect functionality of the pexpect module
#it will read data from the the given serial object until encountering any of the given keys
def expect(ser, keys, tout=0):
    line_matcher = re.compile('\n') #implementation assumes we won't have multi-line keys, searches only single lines
    matchers = []
    for key in keys:
        matchers.append(re.compile(key))
    last_line_ind = 0 #start at the first char
    start = time.clock() #reference pt for timeout
    buff =''
    buff += ser.read(128)
    #while not timed out and the keyword has not been found
    while (time.clock() - start) < tout or tout == 0:
        #check the keys in order, return the index in the list if a match is found
        for ind, val in enumerate(matchers):
            if val.search(buff, last_line_ind):
                print buff[last_line_ind:]
                return ind
        #find the most recent newline char in the buffer
        newline = line_matcher.search(buff, last_line_ind)
        #if one is found, update index of last newline
        if newline:
            print buff[last_line_ind:newline.start(0)]
            last_line_ind = newline.end(0)
        buff += ser.read(128)
    print buff[last_line_ind:]
    #timeout
    return -1

#checks the status of the gumstix board, returns -1, 0 or 1 for error, at login, or logged in respectively
def status(ser):
    #check if any data is flowing
    if expect(ser, ['\w'], 10) != -1:
        login = expect(ser, ['login:'], 150)
        return login
    #prompt data if none is coming
    ser.write('\r')
    #check if at login or logged in
    stat = expect(ser, ['login:', '[$]', '[#]'], 10)
    #timeout
    if stat == -1:
        #check data is flowing
        data = expect(ser, ['\w'], 5)
        if data == 0:
            #if there is data, wait 2.5 mins to get to login
            login = expect(ser, ['login:'], 150)
            return login
        return -1
    elif stat == 1:
        ser.write('sudo su\r')
        expect(ser, ['acomms:'], 10)
        ser.write('acomms\r')
        expect(ser, ['[#]'], 5)
        return 1
    elif stat == 2:
        return 1
    else:
        return 0

#log into board, return 0 for failure, 1 for success
def login(ser):
    #get current status of board
    stat = status(ser)
    #error
    if stat == -1:
        print 'There was an error while attempting to log into the board, please cycle power to reboot.'
        return 0
    #at login
    elif stat == 0:
        ser.write('acomms\r')
        expect(ser, ['Password:'], 10)
        ser.write('acomms\r')
        success = expect(ser, ['[$]'], 10)
        #login attempt failed
        if success == -1:
            print 'There was an error while attempting to log into the board, please cycle power to reboot'
            return 0
        #sudo su
        ser.write('sudo su\r')
        expect(ser, ['acomms:'], 10)
        ser.write('acomms\r')
        expect(ser, ['[#]'], 10)
    #Board logged in!
    return 1

#convenience function for failing a test, closing serial ports, and exiting
def fail(serials=[]):
    for ser in serials:
        ser.close()
    print 'FAILED'
    sys.exit()
