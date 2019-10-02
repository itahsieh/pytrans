#!/bin/sh

rsync -av -e ssh moxa@192.168.4.127:/home/moxa/pytrans/* ./
