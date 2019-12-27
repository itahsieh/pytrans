#!/usr/bin/env python3
# sudo apt install python3-pip
# prerequisite: pip3 install pyserial

debug = 1
if debug:
    import matplotlib.pyplot as plt
    Spec_figsize = (16, 12)
    Spec_dpi = 80

import struct
import time
from sys import path
path.append('./lib')

from MA_utilities import bcolors
from MA_serial import SendCommand, SerialConnect

def RawAverage(ser_port, instruction_str):  
    buffer_size = 1400
    # time interval to take calculating average, in seconds 
    AverageInterval = 1.
    
    input( bcolors.HEADER +
        instruction_str + ', it will take ' + str(AverageInterval) + ' secs to calculate average\n' +
        bcolors.ENDC +
        "Press Enter to continue...")

    count = 0; Xmean = 0.; Ymean = 0.; Zmean = 0.
    
    Zarray = []
    
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
                
                count += 1
                Xmean += raw_float[0]
                Ymean += raw_float[1]
                Zmean += raw_float[2]
                
                Zarray.append(raw_float[2])
        
        if (time.time() - T_start) > AverageInterval:
            break
    
    SendCommand( ser_port, 'S')
    
    Xmean /= float(count)
    Ymean /= float(count)
    Zmean /= float(count)

    print('Means of X, Y, Z:', Xmean, Ymean, Zmean,'\n')
    
    if debug:
        fig, axes = plt.subplots( figsize = Spec_figsize, dpi = Spec_dpi)
        axes.plot(Zarray)
        axes.set(xlabel='Record number', 
                 ylabel = 'acceleration',
                 title='Time series of Z-acceleration')
        axes.grid(True)
        
    return Xmean, Ymean, Zmean


ser = SerialConnect("/dev/ttyUSB0", 19200)
SendCommand( ser, 'S')
SendCommand( ser, 'RAW')

X1, Y1, Z1 = RawAverage( ser, 'Place in the first position')
X2, Y2, Z2 = RawAverage( ser, 'Rotate 180 degrees along X-axis')
X3, Y3, Z3 = RawAverage( ser, 'Rotate 180 degrees along Y-axis')

ser.close()

Xbias = 0.5*(0.5*(X1+X2) + X3)
Ybias = 0.5*(0.5*(Y2+Y3) + Y1)
Zbias = 0.5*(0.5*(Z1+Z3) + Z2)

print('bias:', Xbias, Ybias, Zbias)

BiasFile = open( "bias.dat", "a")
BiasFile.write( 
    '{:f} {:f} {:f}\n'.format( Xbias, Ybias, Zbias)
    )
BiasFile.close()

if debug:
    plt.show()



