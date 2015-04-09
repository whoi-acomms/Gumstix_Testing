#dependencies="00a"
__author__ = 'chet'
#
# $Id$
#

import gumtools as gt
import serial
from labjack import ljm
from time import sleep

ser = serial.Serial(port='COM7', baudrate=115200, timeout=1)
if not gt.login(ser):
    gt.fail(ser)
#open the labjack with the specified serial # on any available connection
lj = ljm.open(ljm.constants.dtANY, ljm.constants.ctANY, "470010285")
gpios = []
#iterate over all GPIOs
for i in xrange(8):
    gpios.append(True)
    #just to save copiable code, loop over I/O 0 or 1
    for val in xrange(2):
        #VERY IMPORTANT always reset LJ to low out to avoid driving LJ and Gumstix simultaneously
        DIO = "FIO%i" % i
        ljm.eWriteName(lj, DIO, 0)
        #configure GPIO to output
        ser.write('echo out > /gpio/boardio%i/direction\r' % (i+1))
        sleep(1)
        ser.write('echo %i > /gpio/boardio%i/value\r' % (val, i+1))
        sleep(1)
        #read value on LJ
        ljread = int(ljm.eReadName(lj, DIO))
        print 'LJRead on GPIO %i expecting %i got %i' % (i, val, ljread)
        if ljread != val:
            gpios[i] = False
        ser.write('echo in > /gpio/boardio%i/direction\r' % (i+1))
        #configure LJ to output
        ljm.eWriteName(lj, DIO, val)
        sleep(1)
        #read value on gumstix
        ser.write('cat /gpio/boardio%i/value\r' % (i+1))
        gtread = gt.expect(ser, ['0', '1'], 5)
        print 'GTRead on GPIO %i expecting %i got %i' % (i, val, gtread)
        if gtread != val:
            gpios[i] = False
#pass if all passed
success = True
#print results for each GPIO
for ind, gpio in enumerate(gpios):
    if gpio:
        result = 'passed'
    else:
        result = 'failed'
        success = False
    print 'GPIO %i %s' % (ind, result)
#fail if any one failed
if not success:
    gt.fail(ser)
ser.close()
lj.close()
print 'PASSED'
