#!/bin/bash -vf
#
# $Id$
#

#Turn off Ethernet and WLAN
ifdown eth0
ifdown wlan0

# Turn off subsystems
echo 0 > /gpio/power-ethernet/value
echo 0 > /gpio/power-display/value
echo 0 > /gpio/power-5v/value
echo 0 > /gpio/power-sdcard/value

#Disbale Ethernet
modprobe -r smsc911x

# Disable Wifi
modprobe -r libertas_sdio
sleep 5
echo 0 > /sys/class/gpio/gpio16/value

# Disable Bluetooth
echo 0 > /sys/class/gpio/gpio164/value


sleep 60

#Enable subsystems
echo 1 > /gpio/power-ethernet/value
echo 1 > /gpio/power-display/value
echo 1 > /gpio/power-5v/value
echo 1 > /gpio/power-sdcard/value

#Enable Wifi
echo 1 > /sys/class/gpio/gpio16/value
sleep 5
modprobe libertas_sdio
sleep 5
modprobe libertas_sdio

# Enable Bluetooth
echo 1 > /sys/class/gpio/gpio164/value

sleep 5
ifup wlan0
ifup eth0
