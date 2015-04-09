#!/bin/bash -vf
#
# $Id$
#

stty -F $1 115200
sleep 1
echo 1234 > $1
sleep 5
cat $1
