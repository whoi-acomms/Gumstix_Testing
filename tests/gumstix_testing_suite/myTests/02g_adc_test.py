#dependencies="00a"
__author__ = 'chet'
#
# $Id$
#
import gumtools as gt
import serial
import re
import operator

#open the port and login
ser = serial.Serial(port="COM7", baudrate=115200, timeout=1)
if not gt.login(ser):
    gt.fail(ser)
#start the adc test
ser.write("tests/gumstix_adc_test.sh\r")
#wait until the only output will be adc reads
gt.expect(ser, ["gumstix_adc_test.sh"], 10)
#collect all lines of adc reads into buff
buff = ser.read(128).decode('utf-8')
endread = re.search('[a-zA-Z]', buff)
while not endread:
    buff += ser.read(128).decode('utf-8')
    endread = re.search('[a-zA-Z]', buff)
#ignore anything after the adc reads
buff = buff[:endread.start()]
#now check to make sure each column of the reads changes at some point
firstvals = []
bools = []
for line in buff:
    for ind,val in enumerate(line.split(' ')):
        #first line initialize the boolean and firstval lists
        if len(bools) <= ind:
            bools.append(False)
            firstvals.append(val)
        #every other iteration, check the current value against the first
        else:
            if firstvals[ind] != val:
                bools[ind] = True
#reduce our list of booleans to a single pass or fail
if not reduce(operator.or_, bools, False):
    gt.fail(ser)
ser.close()
print 'PASSED'
