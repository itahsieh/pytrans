#!/usr/bin/env python
from ser_conf import *
from MA_serial import ListConfig
import ser_par as sp


for BaudRate in [ 115200, 256000, 921600]:
    ser_port = ser_config(BaudRate)
    if ser_port != -1:
        print 'Connect successfully! Baud Rate = ', BaudRate
        ser_port.close()
        Current_BaudRate = BaudRate
        break
    
if Current_BaudRate != sp.baud_rate:
    ser_port = ser_config(Current_BaudRate)
    if sp.baud_rate == 921600:
        baud_id = 7
    elif sp.baud_rate == 115200:
        baud_id = 3
        
    cmd = 'BAUD'+ str(baud_id)
    print cmd
    SendCommand( ser_port, cmd)
    ser_port.close()


