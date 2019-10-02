#!/usr/bin/env python

import struct
import time
import calendar

from ser_util import SendCommand, SerialConnect

def bytes_xor(bytes_array):
    checksum = b'\x00'
    for i in range(len(bytes_array)):
        checksum = chr(ord(checksum) ^ ord(bytes_array[i]))
    return checksum

SamplingRate = 100.
# time interval to take calculating average, in seconds 
TimeInterval = 2.
# maximum records within the time interval
max_record = int(TimeInterval * SamplingRate)
buffer_size = 14 * 10

tcp_pack = bytearray(b'0'*1224)
tcp_raw = bytearray(b'0'*1200)





ser_port = SerialConnect("/dev/ttyM0", 19200)
SendCommand( ser_port, 'S')
SendCommand( ser_port, 'RAW')

# flush out serial data (wait untill all data is written)
ser_port.flush()
# restart serial streaming
SendCommand( ser_port, 'RS')
# get rid of the leading n records, in case of the firmware buffer (supposed to be 1 record) 
# ( n * 14 bytes for raw data mode) 
#ser_port.read(10 * 14 )


b_count = 0
n_record = 0
T_start = time.time()
while True:
    due = False
    
    if n_record == 0:
        captured = time.time()
    
    
    b_count += 1
    buffer = ser_port.read(buffer_size)
    raw_list = buffer.split(b'\xa5')
    
    n_list = len(raw_list)

    
    if len(raw_list[0]) > 0:
        print 'warning: byte misalignment at head of buffer',b_count,'heading size:', len(raw_list[0]),len(raw_list[1])
    
    if len(raw_list[-1]) < 13:
        left_data = raw_list[-1]
        
    if 0 < len(raw_list[0]) < 13:
        if b_count != 0:
            assert( len(left_data) + len(raw_list[0]) <= 13 )
            raw_list[0] = left_data + raw_list[0]
    
    #assert(len(raw_list[0]) == 0)
    #assert(len(raw_list[-1] == 13))
    
    for i in range(n_list):
        record = False
        
        # In the case the data between 0xa5
        if len(raw_list[i]) == 13:
            n_record += 1
            record = True
            
            #raw_float = struct.unpack( 'f'*3, raw_list[i][0:12] ) 
            #print raw_float[0], raw_float[1], raw_float[2]
            
            checksum = bytes_xor(raw_list[i][0:12])

            assert(checksum == raw_list[i][12])
            
            raw_record = raw_list[i][0:12] 
            
            if n_record == max_record:
                eclapsed = time.time() - T_start
                due = True
                break
        else:
            if i == 0:
                if len(raw_list[i]) == 0:
                    pass
                else:
                    print 'warning'
            elif i == n_list-1 :
                assert(left_data == raw_list[i])
            else:
                if len(raw_list[i-1]) < 13:
                    pass
                else:
                    n_record += 1
                    record = True
                    #print i, len(raw_list[i])
                    raw_record = raw_list[i] + '\xa5' + raw_list[i+1]
                    if len(raw_record) < 13:
                        raw_record = raw_record+ '\xa5' + raw_list[i+2]
                    assert(len(raw_record) == 13)
                    
                    checksum = bytes_xor(raw_record[0:12])
                    assert(checksum == raw_record[12])
                    

                


        # append the record
        if record == True:
            tcp_raw[(n_record-1)*12:n_record*12] = raw_record
    

    
    if due:
        break

SendCommand( ser_port, 'S')
ser_port.close()

print 'sampling rate:', max_record / eclapsed,'Hz in ',eclapsed, 'seconds: '












