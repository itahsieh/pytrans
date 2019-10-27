#!/bin/sh

rsync -av ./pytrans_a308.py -e ssh moxa@192.168.4.127:/home/moxa/pytrans/* 
rsync -av ~/MachineAnalyzer/lib -e ssh moxa@192.168.4.127:/home/moxa/pytrans/lib 
