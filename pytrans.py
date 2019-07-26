#!/usr/bin/env python3
# sudo apt install python3-pip
# prerequisite: pip3 install pyserial



import struct
import time
from sys import path
path.append('../MachineAnalyzer/lib')

from MA_utilities import bcolors
from MA_serial import SendCommand, SerialConnect

def RawAverage(ser_port, instruction_str):  
    buffer_size = 1400
    # time interval to take calculating average, in seconds 
    AverageInterval = 1.

    
    # flush out serial data (wait untill all data is written)
    ser_port.flush()
    # restart serial streaming
    SendCommand( ser_port, 'RS')
    # get rid of the leading n records, in case of the firmware buffer (supposed to be 1 record) 
    # ( n * 14 bytes for raw data mode) 
    ser_port.read(10 * 14)

    T_start = time.time()
    while True:
        buffer = ser_port.read(buffer_size)
        raw_list = buffer.split(b'\xa5')
        
        for i in range(1,len(raw_list)-1):
            if len(raw_list[i]) == 13:
                raw_float = struct.unpack( 'f'*3, raw_list[i][0:12] ) 
                print(raw_float[0], raw_float[1], raw_float[2]) 
        
        if (time.time() - T_start) > AverageInterval:
            break
    
    SendCommand( ser_port, 'S')
    



ser = SerialConnect("/dev/ttyUSB0", 19200)
SendCommand( ser, 'S')
SendCommand( ser, 'RAW')

RawAverage( ser, 'Place in the first position')


ser.close()






