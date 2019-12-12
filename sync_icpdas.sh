#!/bin/sh

REMOTE_CLIENT='root@192.168.255.1'
ICPDAS_DIR="$REMOTE_CLIENT:/home/root/pytrans/"

ssh $REMOTE_CLIENT /bin/mkdir -p /home/root/pytrans
ssh $REMOTE_CLIENT /bin/mkdir -p /home/root/pytrans/lib

# scp ser_par.py                       $ICPDAS_DIR
scp trans_par.py                       $ICPDAS_DIR
scp ser_conf.py                       $ICPDAS_DIR
scp ser_list.py                       $ICPDAS_DIR
scp pytrans.py                        $ICPDAS_DIR
# scp $HOME/MachineAnalyzer/lib/*.py    $ICPDAS_DIR'lib'
