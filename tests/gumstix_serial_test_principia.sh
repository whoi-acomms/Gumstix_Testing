#!/bin/bash
#
# $Id$
#

export TOOLDIR=../tools/serial_testing
export NBYTES=10000
export DEV1=/dev/eser0
export DEV2=/dev/eser1

dd if=principia0.txt count=10000c bs=1 of=principia_tmp.txt

echo Writing the first 10000 bytes of Newton's Principia from /dev/eser0 to /dev/eser1.
../tools/serial_testing/serial_read_test  /dev/eser1 115200 10000 30 5 ./principia_tmp_tx1_rx2.txt &
PID1=$!
../tools/serial_testing/serial_write_test /dev/eser0 115200 ./principia_tmp.txt
wait PID1
echo Done writing. Diff is:
diff -u principia_tmp.txt principia_tmp_tx1_rx2.txt
exit

echo Writing the first 10000 bytes of Newton's Principia from /dev/eser1 to /dev/eser0.
../tools/serial_testing/serial_read_test  /dev/eser0 115200 10000 30 5 ./principia_tmp_tx2_rx1.txt &
PID2=$!
../tools/serial_testing/serial_write_test /dev/eser1 115200 ./principia_tmp.txt
wait PID2
echo Done writing. Diff is:
diff -u principia_tmp.txt principia_tmp_tx2_rx1.txt

