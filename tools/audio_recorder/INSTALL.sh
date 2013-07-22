#!/bin/bash -f

#Standard Variables
INSTALL_DIR=/home/acomms/scripts
CONTROL_FILE_DIR=/home/acomms/fromshore/
SCRIPT_NAME=dorecord.py

THIS_SCRIPT=$INSTALL_DIR/$SCRIPT_NAME

#Custom Variables
RECORDINGS_DIR=/home/acomms/recordings
CONTROL_FILE=$CONTROL_FILE_DIR/recordcmd


#Create Directories
mkdir -p $INSTALL_DIR
mkdir -p $RECORDINGS_DIR
mkdir -p $CONTROL_FILE_DIR

#Copy File
cp -af $SCRIPT_NAME $INSTALL_DIR/.

#Turn off Recorder
echo "off" > $CONTROL_FILE

#Install in Cron
(crontab -l| grep -v $THIS_SCRIPT ; echo "@reboot python ${THIS_SCRIPT}") | uniq | crontab