import platform, sys
import ser_par as sp

# Pre-check
if 'Raw' in sp.output_mode:
    Estimated_BaudRate = sp.sampling_rate * 3 * 4 * 10
    if Estimated_BaudRate < BaudRate:
        print 'warning: estimated baud rate is',Estimated_BaudRate
        sys.exit(1)

if platform.machine() == 'x86_64':
    Port = '/dev/ttyUSB0'
    sys.path.append('/home/vandine/MachineAnalyzer/lib')
elif platform.node() == 'Moxa':
    Port = '/dev/ttyM0'
    sys.path.append('/home/moxa/pytrans/lib')
    sys.path.append('/home/moxa/pytrans')
elif platform.node() == 'LP-5231':
    Port = '/dev/ttyO4'
    sys.path.append('/home/root/pytrans/lib')
    sys.path.append('/home/root/pytrans')
else:
    print('Port is not defined')
    sys.exit(1)

from MA_serial import *


def ser_config(BaudRate):    
    if sp.sensor_type == 'A308':
        if BaudRate == 115200:
            pass
        elif BaudRate == 921600:
            pass
        else:
            print 'BaudRate is not supported:', BaudRate
    else:
        print 'sensor_type is not recognized:', sp.sensor_type
        sys.exit(1)
    
    print 'Port:', Port, 'Baud Rate:', BaudRate

    ser_port = SerialConnect(Port, BaudRate)
    ser_port.flush()
    SendCommand( ser_port, 'S')
    
    sensor_conf = sensor(ser_port, print_out = False)
    
    if not hasattr(sensor_conf, 'version'):
        print 'sensor is not detected'
        return -1

    if 'RAW' in sp.output_mode:
        if 'Feature' in sp.output_mode:
            if 'FFT' in sp.output_mode:
                ODE_ID = 7
            else:
                ODE_ID = 5
        else:
            if 'FFT' in sp.output_mode:
                ODE_ID = 6
            else:
                ODE_ID = 4
    else:
        if 'Feature' in sp.output_mode:
            if 'FFT' in sp.output_mode:
                ODE_ID = 3
            else:
                ODE_ID = 1
        else:
            if 'FFT' in sp.output_mode:
                ODE_ID = 2
            else:
                print 'The output mode is missing or unrecognized'
                exit()
    SendCommand(ser_port,'ODE'+str(ODE_ID))    
            
    # check and set sampling rate     
    if int(sensor_conf.SamplingRate[0]) != sp.sampling_rate:
        print('reset sampling rate')
        if sp.sampling_rate == 4000:
            ODR_ID = 0
        elif sp.sampling_rate == 2000:
            ODR_ID = 1
        elif sp.sampling_rate == 1000:
            ODR_ID = 2
        elif sp.sampling_rate == 500:
            ODR_ID = 3
        elif sp.sampling_rate == 250:
            ODR_ID = 4
        elif sp.sampling_rate == 125:
            ODR_ID = 5
        else:
            print('Sampling rate is not defined:',sp.sampling_rate)
            sys.exit(1)
        SendCommand(ser_port,'ODR'+str(ODR_ID))
        
    return ser_port


