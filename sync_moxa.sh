#!/bin/sh

MOXA_DIR='-e ssh moxa@192.168.4.127:/home/moxa/pytrans/'

rsync -av pre_install.sh                    $MOXA_DIR
rsync -av ser_conf.py                       $MOXA_DIR
rsync -av ser_list.py                       $MOXA_DIR
rsync -av pytrans.py                        $MOXA_DIR
rsync -av $HOME/MachineAnalyzer/lib/*.py    $MOXA_DIR'lib'
 
