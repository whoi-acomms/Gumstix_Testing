#!/bin/bash -f
#
# $Id$
#

#This configures the GPS at boot time. 

GPS_SERIAL=/dev/ttyO0
GPS_BAUDRATE=19200
GPS_GPIO=/sys/class/gpio/gpio225

#Setup serial device
#setserial $GPS_SERIAL low_latency
stty $GPS_BAUDRATE -F $GPS_SERIAL

#Power on GPS
echo out > $GPS_GPIO/direction
echo 1 > $GPS_GPIO/value

#Cycle gpsd
/etc/init.d/gpsd restart
