#!/bin/bash -f
#
# $Id$
#

echo "Gumstix Audio Recording Test"
echo ""
read -p "Press any key to start Recording for 5 secs... " -n1 -s
echo ""
arecord -f S16_LE -c2 -r48000 -t wav -d 5 test.wav
echo ""
read -p "Press any key to playback Recording..." -n1 -s
echo ""
aplay test.wav
rm -f test.wav 

