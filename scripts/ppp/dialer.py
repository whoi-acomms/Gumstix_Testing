'''
Created on May 14, 2011

@author: Eric Gallimore
'''
# Stupid simple script to try to dial the Iridium modem a few times
# $Id$

import os
import time
import logging

# Configure logging
logformat = logging.Formatter("%(asctime)s\t%(levelname)s\t%(message)s", "%Y-%m-%d %H:%M:%S")
logger = logging.getLogger("ppp-dialer")
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('/var/log/ppp-dialer.log')
fh.setLevel(logging.DEBUG)
fh.setFormatter(logformat)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(logformat)
logger.addHandler(fh)
logger.addHandler(ch)

DIAL_ATTEMPTS = 3   # Number of times to try connecting
WAIT_SECONDS = 90  # Wait this long between redial attempts
LAST_OCTET = '52'	#Board ID Number, this needs to be modified each installation. 

# We need to create this dev node after every reboot for some reason
os.system('mknod /dev/ppp c 108 0')
os.system('echo 224 > /sys/class/gpio/export')
os.system('echo out > /sys/class/gpio/gpio224/direction')
os.system('echo 228 > /sys/class/gpio/export')
os.system('echo out > /sys/class/gpio/gpio228/direction')

# Make sure that we don't have any leftover sync or rsync processes
os.system('pkill -f syncfiles')
os.system('pkill -f rsync')


# Try to redial a few times
for i in range(DIAL_ATTEMPTS):
    #Toggle power, just to be safe
    os.system('echo 1 > /sys/class/gpio/gpio224/value')
    time.sleep(15)
    os.system('echo 1 > /sys/class/gpio/gpio228/value')
    time.sleep(0.1)
    os.system('echo 0 > /sys/class/gpio/gpio228/value')
    time.sleep(10)    

    logger.info("Running pppd, attempt " + str(i) + " of " + str(DIAL_ATTEMPTS))
    
    retcode = os.system('/usr/sbin/pppd nodetach call shore 10.0.2.'+LAST_OCTET+':')
    exitcode = (retcode >> 8) & 0xFF    #This is some os.system weirdness.  Another reason for subprocess...
    
    logger.info("PPPD exited with code " + str(exitcode))
    
    # Also, turn the power off
    os.system('echo 0 > /sys/class/gpio/gpio224/value')


    # See if the rsync script (or a local user) told it to terminate
    if (exitcode == 5):
        logger.info("Success? User terminated PPPD, no more retries")
        break
    
    # If it failed for another reason, wait a few minutes and try again.
    time.sleep(WAIT_SECONDS)
    
# Once we are here, we either succeeded or ran out of redials.
logger.info("Dialing session complete.")
    

