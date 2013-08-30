#!/bin/bash -f

arecord -f S16_LE -c2 -r48000 -t wav -d 5 test.wav &
aplay /home/acomms/tests/audiocheck.net_L.wav
aplay /home/acomms/tests/audiocheck.net_R.wav
sleep 5
aplay test.wav
rm -f test.wav 

