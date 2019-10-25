#!/usr/bin/env python
import serial
from ser_util import *

Port = '/dev/ttyUSB0'
BaudRate  = 115200

ser = SerialConnect( Port, BaudRate)
ListConfig(ser)
ser.close()
