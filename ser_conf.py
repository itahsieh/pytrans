from ser_par import *
import platform, sys

if platform.machine() == 'x86_64':
    Port = '/dev/ttyUSB0'
    sys.path.append('/home/vandine/MachineAnalyzer/lib')
elif platform.node() == 'Moxa':
    Port = '/dev/ttyUSB5'
    sys.path.append('/home/moxa/pytrans/lib')
    sys.path.append('/home/moxa/pytrans')
else:
    print('Port is not defined')
    sys.exit(1)

from MA_serial import *


def ser_config():    
    if sensor_type == 'A308':
        BaudRate = 115200
    elif sensor_type == 'hanxi':
        BaudRate = 19200
    
    print 'Port:', Port, 'Baud Rate:', BaudRate
    
    ser_port = SerialConnect(Port, BaudRate)
    ser_port.flush()
    SendCommand( ser_port, 'S')
    sensor_conf = sensor(ser_port, print_out = False)
    
    
    if not hasattr(sensor_conf, 'SamplingRate'):
        print 'sensor is not detected'
        sys.exit(1)

    '''
    # check and set output mode
    for i in range(len(output_seq)):
        # use exclusive or to turn on/off output mode
        if (output_seq[i] in sensor_conf.output) != (output_seq[i] in output_mode):
            if output_seq[i] == 'Feature':
                SendCommand( ser_port, 'FEA')
            elif output_seq[i] == 'RAW':
                SendCommand( ser_port, 'RAW')
            elif output_seq[i] == 'FFT':
                SendCommand( ser_port, 'FFT')
            #print('{:s} {:s}'.format( output_seq[i], 'turns off' if output_seq[i] in sensor_conf.output else 'turns on'))
    '''
    
    if 'RAW' in output_mode:
        if 'Feature' in output_mode:
            if 'FFT' in output_mode:
                ODE_ID = 7
            else:
                ODE_ID = 5
        else:
            if 'FFT' in output_mode:
                ODE_ID = 6
            else:
                ODE_ID = 4
    else:
        if 'Feature' in output_mode:
            if 'FFT' in output_mode:
                ODE_ID = 3
            else:
                ODE_ID = 1
        else:
            if 'FFT' in output_mode:
                ODE_ID = 2
            else:
                print 'The output mode is missing or unrecognized'
                exit()
    SendCommand(ser_port,'ODE'+str(ODE_ID))    
            
    # check and set sampling rate     
    if int(sensor_conf.SamplingRate[0]) != sampling_rate:
        print('reset sampling rate')
        if sampling_rate == 4000:
            ODR_ID = 0
        elif sampling_rate == 2000:
            ODR_ID = 1
        elif sampling_rate == 1000:
            ODR_ID = 2
        elif sampling_rate == 500:
            ODR_ID = 3
        elif sampling_rate == 250:
            ODR_ID = 4
        elif sampling_rate == 125:
            ODR_ID = 5
        else:
            print('Sampling rate is not defined:',sampling_rate)
            sys.exit(1)
        SendCommand(ser_port,'ODR'+str(ODR_ID))
        
    return ser_port


