#!/bin/bash -f
#This is not executable script. 
#
# $Id$
#
exit -1

#Thanks to 
#http://www.rjsystems.nl/en/2100-ntpd-garmin-gps-18-lvc-gpsd.php


#Install necessary packages:
apt-get install gpsd gpsd-clients libgps20 python-gps ntp

#Reconfigure GPSD to the correct setting
dpkg-reconfigure gpsd
#		Start gpsd automatically on boot? 
#			Yes
#		Device the GPS receiver is attached to: 
#			/dev/ttyO0
#		Should gpsd handle attached USB GPS receivers automatically? 
#			No
#		Options to gpsd: 
#			-n
#		GPSD control socket path:
#			{leave as suggested}

#To test gpsd
killall gpsd
gpsd -n -N -D2 /dev/ttyO0

#To verify GPS is working
gpspipe -r

#Edit /etc/ntp.conf
Add 
	server 127.127.28.0 minpoll 4 prefer
	fudge  127.127.28.0 time1 0.420 refid GPS
	#server 127.127.28.1 minpoll 4 prefer
	#fudge  127.127.28.1 refid PPS

Restart NTP
	/etc/init.d/ntp restart
	
#Check NTP Status
ntpq -p

#Add GPS_init to crontab
#@reboot /home/acomms/scripts/gps_init.sh
	
