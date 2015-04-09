#dependencies="00a"
__author__ = 'chet'
#
# $Id$
# $HeadURL$
#
import gumtools as gt
import serial
import datetime, time

#open serial one
ser =serial.Serial(port='COM7', baudrate='115200', timeout=1)
#login
if not gt.login(ser):
    gt.fail([ser])
#get the UTC time and convert to a usable string
t=datetime.datetime.utcnow()
tstr = t.strftime('%d %b %Y %H:%M:%S')
#set the date
ser.write('date -s "%s"\r' % tstr)
gt.expect(ser, ['[#]'], 5)
#flush it
ser.write('hwclock -w\r')
gt.expect(ser, ['[#]'], 5)
#reboot and login again
ser.write('reboot\r')
gt.login(ser)
#get the date again (not UTC, because time.mktime seems to assume the
# given time tuple is local time when converting to seconds since epoch
dt = datetime.datetime.now()
texpect = time.mktime(dt.timetuple())
#set up a range of 100 seconds on either side
trange = [texpect-100, texpect, texpect+100]
#trim down to match up to the hundred seconds
for ind, secs in enumerate(trange):
    secs = str(secs)[:-4]
    trange[ind] = secs
#print seconds since epoch on gumstix
ser.write('date +%s\r')
#compare output with expected
clock = gt.expect(ser, trange, 5)
if clock == -1:
    gt.fail([ser])
ser.close()
print 'PASSED'
