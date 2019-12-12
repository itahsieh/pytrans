#!/bin/bash

PRE_INSTALL=0
DEPLOY=0
TEST=1

REMOTE_CLIENT='moxa@192.168.4.127'
REMOTE_DIR="/home/moxa/pytrans/"
SSHPASS='sshpass -p moxa'


sudo ifconfig wlp59s0:1 192.168.4.10 netmask 255.255.255.0

if [ "$PRE_INSTALL" = 1 ]
then
# load prerequisite
$SSHPASS ssh -o StrictHostKeyChecking=no -T $REMOTE_CLIENT <<'ENDSSH'

    # add an IP 
    echo 'moxa' | sudo -S /sbin/ifconfig eth1:1 192.168.1.199 netmask 255.255.255.0 
    # add Gateway to connect outer net
    sudo /sbin/route add default gw 192.168.1.1
    
    # update software list
    sudo apt-get update 
    
    # install python dependancies
    echo 'Y' | sudo apt-get install python python-serial

ENDSSH
fi


# Deploy pytrans
if [ "$DEPLOY" = 1 ]
then
$SSHPASS ssh $REMOTE_CLIENT mkdir -p REMOTE_DIR
$SSHPASS ssh $REMOTE_CLIENT mkdir -p REMOTE_DIR'lib'
echo 'REOMOTE FOLDER CREATED'
$SSHPASS scp ser_par.py    $REMOTE_CLIENT:$REMOTE_DIR
$SSHPASS scp ser_conf.py   $REMOTE_CLIENT:$REMOTE_DIR
$SSHPASS scp ser_list.py   $REMOTE_CLIENT:$REMOTE_DIR
$SSHPASS scp pytrans.py    $REMOTE_CLIENT:$REMOTE_DIR
echo 'PYTRANS TRANSDERING DONE'
$SSHPASS scp trans_par_murano.py            $REMOTE_CLIENT:$REMOTE_DIR'trans_par.py'
$SSHPASS scp murano_activate_io_config.py   $REMOTE_CLIENT:$REMOTE_DIR
echo 'PYTRANS TRANSDERING DONE'
$SSHPASS scp $HOME/MachineAnalyzer/lib/*.py $REMOTE_CLIENT:$REMOTE_DIR'lib/'
echo 'LIBRARY TRANSDERING DONE'
$SSHPASS scp rc.local           $REMOTE_CLIENT:$REMOTE_DIR
$SSHPASS scp watchdog_4g        $REMOTE_CLIENT:$REMOTE_DIR
$SSHPASS scp watchdog_pytrans   $REMOTE_CLIENT:$REMOTE_DIR
echo 'STARTUP PROGRAM TRANSDERING DONE'
fi


# testing RS-232 connectivity
if [ "$TEST" = 1 ]
then
$SSHPASS ssh -T $REMOTE_CLIENT <<'ENDSSH'
    echo 'moxa' | sudo -S chmod 777 /dev/ttyUSB0
    /home/moxa/pytrans/ser_list.py  
ENDSSH
fi



