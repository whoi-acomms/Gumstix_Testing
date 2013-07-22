#!/bin/bash -vf

#Custom Variables
RECORDINGS_DIR=/home/acomms/recordings
STORAGE_LOCATION=/dev/sdb1

#Install in FSTAB
(cat /etc/fstab| grep -v $RECORDINGS_DIR ; echo "${STORAGE_LOCATION} ${RECORDINGS_DIR}  vfat rw        0 0") | uniq > /etc/fstab