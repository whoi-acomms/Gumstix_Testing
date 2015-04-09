#!/bin/bash
#
# $Id$
#

for pkg in `dpkg -- get-selections | grep -v deinstall | awk '{print $1}' | grep -v '(dpkg|apt)'`;
do apt-get -y install --reinstall $pkg; done
