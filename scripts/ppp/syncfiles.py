'''
Script to rsync data to and from shore

This is meant to be called by pppd during ip-up

Created on May 14, 2011

@author: Eric Gallimore
'''

import os
import logging
import datetime

#change me per glider
ONSHORE_LOC = 'glider52/'

# Configure logging
logformat = logging.Formatter("%(asctime)s\t%(levelname)s\t%(message)s", "%Y-%m-%d %H:%M:%S")
logger = logging.getLogger("syncfiles")
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('/var/log/syncfiles.log')
fh.setLevel(logging.DEBUG)
fh.setFormatter(logformat)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(logformat)
logger.addHandler(fh)
logger.addHandler(ch)

incoming_path = '/home/acomms/fromshore'
outgoing_path = '/home/acomms/toshore'

# write the current time to a file that will be sent to the shore
synctimefile = open(outgoing_path + '/synctime', 'a')
try:
    synctimefile.write(datetime.datetime.now().isoformat(' ') + '\n')
finally:
    synctimefile.close()

# rsync the data to shore
logger.info("Starting rsync TO shore")
os.system('rsync -zrv --progress --append --log-file=/var/log/rsync-out.log ' + outgoing_path + '/* 10.0.2.16::'+ ONSHORE_LOC+ '/toshore/')

# Get command files from shore
logger.info("Starting rsync FROM shore")
os.system('rsync -zru --append --progress --log-file=/var/log/rsync-in.log --delete 10.0.2.16::'+ ONSHORE_LOC+ '/fromshore/* '+ incoming_path)

#Do it again

# rsync the data to shore
logger.info("Starting rsync TO shore")
os.system('rsync -zr --append --progress --log-file=/var/log/rsync-out.log ' + outgoing_path + '/* 10.0.2.16::'+ ONSHORE_LOC+ '/toshore/')

# Get command files from shore
logger.info("Starting rsync FROM shore")
os.system('rsync -zru --append --progress --log-file=/var/log/rsync-in.log --delete 10.0.2.16::'+ ONSHORE_LOC+ '/fromshore/* '+ incoming_path)


# See if we got a script that we need to run
if (os.path.exists(incoming_path + '/runme.py') == True):
    logger.info("Found command script, running it...")
    os.system('/usr/bin/python ' + incoming_path + '/runme.py')
    
logger.info("Sync done.  Disconnecting...")

# Kill pppd by sending it a SIGINT, which will tell it to exit gracefully.
os.system('killall -INT pppd')

logger.info("pppd killed.  Done.")

