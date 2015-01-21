#!/bin/bash -f

#setup directories to mount the card on
mkdir /media/sd
mkdir /media/usbhost

#1MB file of random data
#head -c 1048576 /dev/urandom > /home/acomms/tests/test.txt
head -c 1024 /dev/urandom > /home/acomms/tests/test.txt

#get the md5 checksum of the file on the board
boardsum=`md5sum /home/acomms/tests/test.txt | awk '{print $1}'`

#mount over the usb cable
mount /dev/sda1 /media/usbhost

#copy to the mounted location
cp /home/acomms/tests/test.txt /media/usbhost/test.txt

#flush to hardware
sync
sleep 1

#unmount usb
umount /media/usbhost

#mount the card directly
mount /dev/mmcblk1p1 /media/sd

#verify the file was flushed to hardware by getting the checksum from the card
cardsum=`md5sum /media/sd/test.txt | awk '{print $1}'`

#unmount the card
umount /media/sd

#remount usb
mount /dev/sda1 /media/usbhost

#get the sum over usb
usbsum=`md5sum /media/usbhost/test.txt | awk '{print $1}'`

#copy the file back from usb to the board
cp /media/usbhost/test.txt /home/acomms/tests/test2.txt

#remove the copy from usb
rm /media/usbhost/test.txt
sync
sleep 1

#unmount again
umount /media/usbhost

#get the checksum for the file copied from usb to the board
readsum=`md5sum /home/acomms/tests/test2.txt | awk '{print $1}'`

#remove the board copies
rm /home/acomms/tests/test2.txt
rm /home/acomms/tests/test.txt

#verify all checksums match
if [ "$boardsum" = "$cardsum" ] && [ "$boardsum" = "$usbsum" ] && [ "$boardsum" = "$readsum" ]
then
  echo "PASSED"
else
  echo "FAILED"
fi
