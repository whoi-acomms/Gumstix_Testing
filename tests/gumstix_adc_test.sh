#!/bin/bash -f
#
# $Id$
#

/home/acomms/tests/adc-test -d1 2 3 4 5 6 7 | awk '/Read/ {for(i=3; i<=8; i++) printf $i " "; print $NF'} > myoutput.txt &
awkpid=$!
adcpid=`jobs -p`
sleep 10
kill "$adcpid"
cat myoutput.txt
rm myoutput.txt
