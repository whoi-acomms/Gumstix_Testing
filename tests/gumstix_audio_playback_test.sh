#!/bin/bash -vf
#
# $Id$
#

echo "Playing Left Speaker"
aplay audiocheck.net_L.wav
sleep 5
echo "Playing Right Speaker"
aplay audiocheck.net_R.wav
