#!/bin/bash -f

# set the wake time for the RTC to 30 seconds from now
sudo echo 0 > /sys/class/rtc/rtc0/wakealarm
sudo date +"%s" --date='30 seconds' > /sys/class/rtc/rtc0/wakealarm

# hibernate the Gumstix
sudo /sbin/devmem2 0x200002A h 0x5154

