#!/bin/bash -f

#open the serial port, turn off echo and CR to NL
stty -F $1 $2 -echo -icrnl -inlcr -ocrnl -onlcr

#</dev/urandom tr -dc A-Za-z0-9 | head -c 1048576 > test.txt
#< /dev/urandom tr -dc A-Za-z0-9 | head -c 524288 > test.txt
#echo -e "\n" >> test.txt
#create a testfile with 1MB of random data
#in small chunks so awk doesn't get mad
for i in {1..4096}
do
  < /dev/urandom tr -dc A-Za-z0-9 | head -c 256 >> test.txt
  echo -e "\n" >> test.txt
done

#Fork a process to send the file
(cat test.txt; echo -e "finished") > $1 &

#Awk through the output until reaching the terminating word
awk '/finished/ {exit} {print}' $1 > ser_test.txt

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
#rm ser_test.txt
#rm test.txt
