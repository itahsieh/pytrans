#!/usr/bin/env python

import struct
import time
import socket
import sys

sys.path.append('/home/vandine/MachineAnalyzer/lib')
from MA_serial import SendCommand, SerialConnect

Port = '/dev/ttyUSB0'
BaudRate = 115200

buffer_size = 132 * 1

ser_port = SerialConnect(Port, BaudRate)

SendCommand( ser_port, 'S')
ser_port.flush()
SendCommand( ser_port, 'FEA')

n_record = 0
left_data = None

# restart serial streaming
SendCommand( ser_port, 'RS')
while True:
    due = False
    
    if n_record == 0:
        captured = time.time()


    

    buffer = ser_port.read(buffer_size)
    raw_list = buffer.split(b'AT')
    
    n_list = len(raw_list)
    '''
    print n_list,
    for i in range(n_list):
        print len(raw_list[i]), 
    print ''
    '''
    for i in range(n_list):
        record = False
        n_bytes = len(raw_list[i])
        
        # if the ideal case ocuur: 130 bytes data
        if n_bytes == 130:
            record = True
            raw_record = raw_list[i]
            n_record += 1
            if i == n_list - 1:
                left_data = None
        else:
            # if the first row is shorter than 130
            if i == 0:
                # empty data due to strip "AT" label
                if n_bytes == 0:
                    if left_data is None:
                        continue
                
                # The case the buffer doesn't begin with "AT"
                if left_data is not None:
                    if n_bytes + len(left_data) == 130:
                        record = True
                        raw_record = left_data + raw_list[i]
                        n_record += 1
            
            # if the last row is shorter than 130
            elif i == n_list-1:
                left_data = raw_list[i]
                continue

            # In case of random "AT" exists inside float data
            elif n_bytes < 130:
                # do nothing after the first fragment
                if len(raw_list[i-1]) < 130:
                    if i != 1:
                        continue
                
                # The fragment occurs: 
                # the first and second are both less 130 bytes
                NBytes_Second =len(raw_list[i+1])
                if NBytes_Second < 130:
                    if n_bytes + 2 + NBytes_Second == 130:
                        record = True
                        raw_record = raw_list[i] + b'AT' + raw_list[i+1]
                        n_record += 1
                    else:
                        if i != n_list - 2:
                            if n_bytes + 2 + NBytes_Second + 2 + len(raw_list[i+2]) == 130:
                                record = True
                                raw_record = raw_list[i] + b'AT' + raw_list[i+1] + b'AT' + raw_list[i+2]
                                n_record += 1
            else: 
                print 'warning'
            

        # The record fetched
        if record == True:
            datatype    = raw_record[0]
            serial_byte = raw_record[1]
            floats_byte = raw_record[2:126]
            check_sum   = raw_record[126:130]
            
            raw_float = struct.unpack( 'f'*31, floats_byte ) 
            x_mean  = raw_float[0]
            x_std   = raw_float[1]
            x_rms   = raw_float[2]
            x_crest = raw_float[3] 
            x_skew  = raw_float[4]
            x_kurt  = raw_float[5]
            x_max   = raw_float[6]
            x_min   = raw_float[7]
            x_p2p   = raw_float[8]
            x_vel   = raw_float[9]
            
            y_mean  = raw_float[10]
            y_std   = raw_float[11]
            y_rms   = raw_float[12]
            y_crest = raw_float[13] 
            y_skew  = raw_float[14]
            y_kurt  = raw_float[15]
            y_max   = raw_float[16]
            y_min   = raw_float[17]
            y_p2p   = raw_float[18]
            y_vel   = raw_float[19]
            
            z_mean  = raw_float[20]
            z_std   = raw_float[21]
            z_rms   = raw_float[22]
            z_crest = raw_float[23]
            z_skew  = raw_float[24]
            z_kurt  = raw_float[25]
            z_max   = raw_float[26]
            z_min   = raw_float[27]
            z_p2p   = raw_float[28]
            z_vel   = raw_float[29]
            
            temp    = raw_float[30]
        
            print x_mean, '\t', y_mean, '\t', z_mean

    # stop serial streaming
    #SendCommand( ser_port, 'S')


SendCommand( ser_port, 'S')
ser_port.close()

#print 'sampling rate:', max_record / eclapsed,'Hz in ',eclapsed, 'seconds: '













