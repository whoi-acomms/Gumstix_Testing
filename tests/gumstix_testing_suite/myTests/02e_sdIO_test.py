#dependencies="00a"
__author__ = 'chet'
import gumtools as gt
import serial
import uuid

#open the port and login to gumstix
ser = serial.Serial(port="COM7", baudrate=115200, timeout=1)
if not gt.login(ser):
    gt.fail(ser)
#create a directory to mount the card to
ser.write('mkdir /media/sd\r')
gt.expect(ser, ['[#]'],3)

#3 mounts and unmounts
for mounts in xrange(3):
    #mount the sdcard
    ser.write('mount /dev/mmcblk1p1 /media/sd\r')
    mnt = gt.expect(ser, ['mount:', '[#]'], 5)
    if (mnt == 0) | (mnt == -1):
        print 'There was an error while mounting the sd card, please verify an SDXC card is mounted in the secondary slot.'
        gt.fail(ser)
    #random file name to save random data
    gumfile = uuid.uuid4().hex
    #write the first MB of data from /dev/urandom to the random file
    ser.write('head -c 1048576 /dev/urandom > %s\r' % gumfile)
    if gt.expect(ser, ['[#]'], 15):
        print 'There was an error while copying data from /dev/urandom to a file on disk. Try rebooting or editing this' \
              'script to use an alternate data source.'
        gt.fail(ser)
    #a list of filenames on the sdcard
    sdfiles = []
    for rw in xrange(3):
        #random destination filename
        sdfiles.append(uuid.uuid4().hex)
        #copy the 1MB file to the card
        ser.write('cp %s /media/sd/%s\r' % (gumfile, sdfiles[rw]))
        if gt.expect(ser, ['[#]'], 10):
            print 'There was an error while writing to the SD card, please try remounting the card and/or rebooting the board.'
            gt.fail(ser)
        #flush buffered data to disk
        ser.write('sync\r')
        if gt.expect(ser, ['[#]'], 15):
            gt.fail(ser)
        #verify that the data was written correctly and we can read it back correctly
        ser.write('diff -s %s /media/sd/%s\r' % (gumfile, sdfiles[rw]))
        checkfile = gt.expect(ser, ['identical', 'differ', 'No such file or directory'])
        #timeout, unanticipated error occurred
        if checkfile == 2:
            print 'There was an error while reading from the SD card, please try remounting the card and/or rebooting the board.'
            gt.fail(ser)
        #the file on the card does not match the file on the rootfs
        elif checkfile == 1:
            print 'The data read from the card does not match the data written to the card.'
            gt.fail(ser)
    #remove all our files from the card
    for sdfile in sdfiles:
        ser.write('rm /media/sd/%s\r' % sdfile)
        if gt.expect(ser, ['[#]'], 5):
            gt.fail(ser)
    ser.write('rm %s' % gumfile)
    if gt.expect(ser, ['[#]'], 5):
        gt.fail(ser)
    #unmount the card
    ser.write('umount /media/sd\r')
    umnt = gt.expect(ser, ['umount: ', '[#]'], 5)
    if (umnt == 0) | (umnt == -1):
        gt.fail(ser)
#If we get here, everything passed
ser.close()
print 'PASSED'