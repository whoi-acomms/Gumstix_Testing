#!/bin/bash -f

#open the serial port, turn off echo and CR to NL
stty -F $1 $2 -echo -icrnl
#Fork a process to send the file
(cat test.txt; echo "finished") > $1 &
#Awk through the output until reaching the terminating word
awk '/finished/ {exit} {print}' $1 > ser_test.txt
#convert /r/n to /n
#dos2unix ser_test.txt
#get md5sums
md5start=`md5sum test.txt | awk '{print $1}'`
md5end=`md5sum ser_test.txt | awk '{print $1}'`
#validate file contents were transferred successfully
if [ "$md5start" = "$md5end" ]
then
  echo "PASSED"
else
  echo "FAILED"
fi
rm ser_test.txt
