#!/bin/bash -vf

#Custom Variables
RECORDINGS_DIR=/home/acomms/recordings
STORAGE_LOCATION=/dev/mmcblk1p1

#Install in FSTAB
(cat /etc/fstab| grep -v $RECORDINGS_DIR ; echo "${STORAGE_LOCATION} ${RECORDINGS_DIR}  vfat rw,noauto,users,exec,dev        0 0") | uniq > /etc/fstab