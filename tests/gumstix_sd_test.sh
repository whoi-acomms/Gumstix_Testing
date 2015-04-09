#!/bin/bash
#
# $Id$
#

mount /dev/mmcblk1p2 /mnt/
touch /mnt/test
echo "helloworld" > /mnt/test 
cat /mnt/test 
rm -f /mnt/test 
umount /mnt
