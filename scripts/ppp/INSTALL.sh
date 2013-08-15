#!/bin/bash -vf

THIS_SCRIPT='/home/acomms/scripts/dialer.py'

#Copy files
cp -af chatscripts/* /etc/chatscripts/.
cp -af peers/ /etc/ppp/peers/.
cp -af ip-up.d/ /etc/ppp/ip-up.d/.
cp -af dialer.py /home/acomms/scripts/.
cp -af syncfiles.py /home/acomms/scripts/.

#Install in Cron
(crontab -l| grep -v $THIS_SCRIPT ; echo "* */1 * * * python ${THIS_SCRIPT}") | uniq | crontab
