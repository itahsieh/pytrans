#!/usr/bin/env python

# sensor type: 'A308' or 'hanxi'
sensor_type = 'A308'
# ouput mode: 'Feature', 'RAW', or 'FFT'
output_mode = ['Feature','RAW']
# sampling rate: 4000, 2000, 1000, 500, 250, 125
sampling_rate = 125

# debug mode
# visualized data
debug = True
vis_datatype = ['x_std',  'y_std',  'z_std',
                'x_skew', 'y_skew', 'z_skew',
                'x_kurt', 'y_kurt', 'z_kurt']
n_vis_data = len(vis_datatype)
n_vis_record = 60



if sensor_type == 'A308':
    BaudRate = 115200
    output_seq = ['Feature','FFT','RAW']
elif sensor_type == 'hanxi':
    BaudRate = 19200

import struct, time, socket, sys, select, platform
from numpy import zeros
from math import sqrt, pow, isnan

if platform.machine() == 'x86_64':
    Port = '/dev/ttyUSB0'
    sys.path.append('/home/vandine/MachineAnalyzer/lib')
elif platform.node() == 'Moxa':
    Port = '/dev/ttyM0'
    sys.path.append('/home/moxa/pytrans/lib')
else:
    print('Port is not defined')
    sys.exit(1)

from MA_serial import *
from MA_utilities import floatbytes_xor


for var in ['array_firm','array_num','array_num2']:
    exec("%s  = zeros((n_vis_data, n_vis_record))" % var)

########################################################3

ser_port = SerialConnect(Port, BaudRate)
ser_port.flush()
SendCommand( ser_port, 'S')
sensor_conf = sensor(ser_port, print_out = False)


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


axis_dict = {'x':0, 'y':1, 'z':2}

######################################################
#           The fetching loop starts                 #
######################################################
n_record = 0.0
left_data = None

# restart serial streaming
SendCommand( ser_port, 'RS')

while True:
    due = False
    
    for data_type in output_seq:
        if data_type in output_mode:
    
            if data_type == 'Feature':
                BufferSize = 132 * 1
                RecordBytes = 130
            elif data_type == 'RAW':
                BufferSize = 1544 * 1
                RecordBytes = 1542
            else:
                print('warning: data type is not defined', data_type)
                sys.exit(1)
                
            buffer = ser_port.read(BufferSize)
            raw_list = buffer.split(b'AT')
            
            n_list = len(raw_list)
            
            '''
            print data_type, n_list,
            for i in range(n_list):
                print len(raw_list[i]),
            print ''
            '''
            
            for i in range(n_list):
                record = False
                n_bytes = len(raw_list[i])
                
                # if the ideal case ocuur: RecordBytes bytes data
                if n_bytes == RecordBytes:
                    record = True
                    raw_record = raw_list[i]
                    if i == n_list - 1:
                        left_data = None
                else:
                    # if the first row is shorter than RecordBytes
                    if i == 0:
                        # empty data due to strip "AT" label
                        if n_bytes == 0:
                            if left_data is None:
                                continue
                        
                        # The case the buffer doesn't begin with "AT"
                        if left_data is not None:
                            if n_bytes + len(left_data) == RecordBytes:
                                record = True
                                raw_record = left_data + raw_list[i]
                    
                    # if the last row is shorter than RecordBytes
                    elif i == n_list-1:
                        left_data = raw_list[i]
                        continue

                    # In case of random "AT" exists inside float data
                    elif n_bytes < RecordBytes:
                        # do nothing after the first fragment
                        if len(raw_list[i-1]) < RecordBytes:
                            if i != 1:
                                continue
                        
                        # The fragment occurs: 
                        # the first and second are both less RecordBytes bytes
                        NBytes_Second =len(raw_list[i+1])
                        if NBytes_Second < RecordBytes:
                            if n_bytes + 2 + NBytes_Second == RecordBytes:
                                record = True
                                raw_record = raw_list[i] + b'AT' + raw_list[i+1]
                            else:
                                if i != n_list - 2:
                                    if n_bytes + 2 + NBytes_Second + 2 + len(raw_list[i+2]) == RecordBytes:
                                        record = True
                                        raw_record = raw_list[i] + b'AT' + raw_list[i+1] + b'AT' + raw_list[i+2]
                                        
                    else: 
                        print 'warning'
                    
                
                # The record fetched
                if record == True:
                    
                    
                    
                    
                    n_record += 1.0 / len(output_mode)
                    datatype    = raw_record[0]
                    serial_byte = raw_record[1]
                    
                    if data_type == 'Feature':
                        assert(datatype == str(b'\x31'))
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
                    
                        #print('{:12.4f} {:12.4f} {:12.4f}'.format(x_mean, y_mean, z_mean))
                        if check_sum[0] != bytes_xor(floats_byte):
                            print('feature checksum is mismatched')
                            
                        if debug:
                            for i in range(n_vis_data):
                                exec("array_firm[i, int(n_record)] = %s" % vis_datatype[i])
                                
                        
                    elif data_type == 'RAW':
                        assert(datatype == str(b'\x33'))
                        floats_byte = raw_record[2:1538]
                        check_sum = raw_record[1538:1542]
                        if check_sum[0] != bytes_xor(floats_byte):
                            print('feature checksum is mismatched')
                        raw_float = struct.unpack( 'f'*384, floats_byte ) 
                        
                        
                        for var in ['value', 'mean', 'std', 'rms', 'crest', 'skew', 'kurt', 'variance', 'kurt2',
                                    'maxi', 'mini', 'p2p', 'square', 'cube', 'diff', 'error']:
                            # declare 3-elements vectors
                            exec("%s = zeros(3)" % var)
                            
                       
                        # skewness = E[(X-mu)^3] / (E([(X-mu)^2])^3/2
                        #          = (E[X^3] - 3 mu std^2 - mu^3) / std^3 
                        # ref: https://en.wikipedia.org/wiki/Skewness
                        
                        #
                        kernel_size = 128
                        for i in range(kernel_size):
                            idx = 3*i
                            for j in range(3):
                                # raw x, y,z value
                                value[j]    = raw_float[idx+j]
                                # raw value square
                                square[j]   = value[j] * value[j]
                                # raw valu cube
                                cube[j]     = square[j] * value[j]
                            
                                mean[j] += value[j]
                                variance[j]  += square[j]
                                if i == 0:
                                    maxi[j] = value[j] 
                                    mini[j] = value[j]
                                else:
                                    maxi[j] = max(maxi[j],value[j])
                                    mini[j] = min(mini[j],value[j])
                                skew[j] += cube[j] 
                                kurt[j] += cube[j] * value[j]
                                
                                
                        for j in range(3):
                            # 1st moment
                            mean[j]     /= kernel_size
                            # 2nd moment
                            variance[j] /= kernel_size
                            # 3rd moment
                            skew[j]     /= kernel_size
                            # 4th moment
                            kurt[j]     /= kernel_size
                            
                            
                            # standard deviation
                            std[j]   = sqrt((variance[j] - mean[j] * mean[j]))
                            rms[j]   = sqrt(variance[j])
                            crest[j] = maxi[j] / rms[j]
                             
                            p2p[j]   = maxi[j] - mini[j]
                            
                            kurt[j]  = kurt[j] \
                                        - 4. * skew[j] * mean[j] \
                                        + 6. * variance[j] * mean[j] * mean[j] \
                                        - 3. * pow(mean[j],4.0)
                            kurt[j]  /= pow(std[j],4.)
                            
                            skew[j]  = (skew[j] - 3.0 * mean[j] * std[j]*std[j] - mean[j] * mean[j] * mean[j] ) \
                                / (std[j]*std[j]*std[j])
                        
                        
                        
                        for i in range(kernel_size):
                            idx = 3*i
                            for j in range(3):
                                # raw x, y,z value
                                value[j]    = raw_float[idx+j]
                                diff[j]     = value[j] - mean[j]
                                kurt2[j]     += pow(diff[j],4.0)
                        
                        for j in range(3):
                            kurt2[j] /= kernel_size * pow(std[j],4.0)
                        
                        
                        
                        print int(n_record), 'th record'
                        if debug:
                            for feature in ['mean','std','rms','crest','skew','kurt','max','min','p2p']:
                                for axis, ax_id in axis_dict.items():
                                    fea_var = axis+'_'+feature
                                    if feature == 'max' or feature == 'min':
                                        raw2fea_var = '%si[%d]' % (feature, ax_id)
                                    else:
                                        raw2fea_var = '%s[%d]' % (feature, ax_id)

                                    exec("fea_val = %s" % (fea_var))
                                    exec("raw2fea_val = %s" % (raw2fea_var))
                                    
                                    if raw2fea_val == 0.0:
                                        exec("error[%d] = %s - %s" % (ax_id, fea_var, raw2fea_var))
                                    else:
                                        exec("error[%d] = (%s - %s) / %s" % (ax_id, fea_var, raw2fea_var, raw2fea_var))

                                    '''
                                    if abs(error[ax_id]) > 1e-2:
                                        exec("print '%s',':',%e,'%s',':',%e" % (fea_var, fea_val, raw2fea_var, raw2fea_val))
                                    '''
                                    
                                    if isnan(error[j]):
                                        print 'Nan occurs at', axis, feature, fea_val, raw2fea_val
                                    
                                #print('{:4s} diff: {:12.3e} {:12.3e} {:12.3e}'.format(feature, error[0], error[1], error[2]) )
                            
                            
                            for i in range(n_vis_data):
                                exec("array_num[i,int(n_record)-1] = %s[%d]" % (vis_datatype[i][2:], axis_dict[vis_datatype[i][0]]) )
                                if vis_datatype[i][2:] == 'kurt': 
                                    exec("array_num2[i,int(n_record)-1] = %s2[%d]" % (vis_datatype[i][2:],axis_dict[vis_datatype[i][0]]) )
                break
    
    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        line = raw_input()
        break

# stop serial streaming
SendCommand( ser_port, 'S')
ser_port.close()


if debug:
    import matplotlib.pyplot as plt
    Spec_figsize = (16, 12)
    Spec_dpi = 80
    
    for i in range(n_vis_data):
        fig, axes = plt.subplots(figsize=Spec_figsize, dpi=Spec_dpi)

        axes.plot(array_firm[i,:], label='firmware')
        axes.plot(array_num[i,:], label='numerical')
        if vis_datatype[2:] == 'kurt':
            axes.plot(array_num2[i,:], label='numerical2')
            axes.set_ylim( top = 5.0, bottom = 0.0)
        axes.set(xlabel='Record number', ylabel = vis_datatype[i], title='Time series of ' + vis_datatype[i])
        axes.legend()
        axes.grid(True)

    plt.show()











