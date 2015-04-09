#!/bin/bash -f
#
# $Id$
#

amixer -q cset iface=MIXER,name="Headset Playback Volume" 2
amixer -q cset iface=MIXER,name="HeadsetL Mixer AudioL1" 1
amixer -q cset iface=MIXER,name="HeadsetL Mixer AudioL2" 1
amixer -q cset iface=MIXER,name="HeadsetL Mixer Voice" 1
amixer -q cset iface=MIXER,name="HeadsetR Mixer AudioR1" 1
amixer -q cset iface=MIXER,name="HeadsetR Mixer AudioR2" 1
amixer -q cset iface=MIXER,name="HeadsetR Mixer Voice" 1
amixer -q cset iface=MIXER,name="DAC2 Digital Fine Playback Volume" 60
amixer -q cset iface=MIXER,name="DAC2 Digital Coarse Playback Volume" 1
