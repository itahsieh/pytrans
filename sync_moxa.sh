#!/bin/sh

MOXA_DIR='-e ssh moxa@192.168.4.127:/home/moxa/pytrans/'


rsync -av pre_install.sh            $MOXA_DIR
rsync -av ./pytrans_a308.py         $MOXA_DIR
rsync -av $HOME/MachineAnalyzer/lib $MOXA_DIR'lib' 
 
