#!/usr/bin/env python

########################################
#       Debug Mode configuration       #
########################################

# debug mode
debug = False

# visualizing ouput: string array with the element 'show' or 'save'
vis_output = ['show','save']
vis_lable = 'static'
# visualized data
#vis_datatype = ['x_std',  'y_std',  'z_std',
                #'x_skew', 'y_skew', 'z_skew',
                #'x_kurt', 'y_kurt', 'z_kurt']
vis_datatype = [ 'z_std',
                 'z_skew',
                 'z_kurt']


#################################
#       Import Libraries        #
#################################
import struct, time, socket, sys, select, platform, os
import datetime


#################################################
# Import serial and  transmission configuration #
#################################################

from ser_conf import *
ser_port = ser_config()

from trans_par import *
'''
if platform.node() == 'Moxa':
    par_file = '/media/sd-mmcblk1p1/VibTrans_Par'
    if os.path.isfile(par_file):
        with open(par_file,'r') as f:
            for line in f.readlines():
                for key in ['trans_interval','trans_adaptive','trans_std_threshold']:
                    if key in line:
                         value = line.rstrip().split('=')[1]
                         exec("%s = %s" % (key,value))
    else:
        print 'VibTrans_Par is not found'
'''
from MA_serial import SendCommand
from MA_utilities import bytes_xor, floatbytes_xor


#########################################
#   parameters initialization           #
#########################################
output_seq = ['Feature','FFT','RAW']
axis_dict = {'x':0, 'y':1, 'z':2}

if csv2sftp_trans:
    import csv, pysftp
    sftp_tmp_dir = '/home/moxa/pytrans/temp'
    if not os.path.exists(sftp_tmp_dir):
        os.makedirs(sftp_tmp_dir)
    
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None 

    srv = pysftp.Connection( 
        host = csv2sftp_host, 
        username = csv2sftp_username,
        password = csv2sftp_password, 
        cnopts=cnopts,
        log = sftp_tmp_dir + "/pysftp.log"
        )
    
    

if murano_trans:
    import murano_par
    import requests
    import json
    try:
        token_filename = murano_par.productid + "_" + murano_par.identifier + "_cik"
        
        if platform.node() == 'Moxa':
            token_filename = '/home/moxa/pytrans/' + token_filename
        with open(token_filename, "r+") as f:
            murano_CIK = f.read()
    except Exception as e:
        print("Unable to read a stored CIK: {}".format(e))
        exit()

if debug:
    import numpy as np
    from math import sqrt, pow, isnan

    n_vis_data = len(vis_datatype)
    for var in ['array_firm','array_num','array_num2']:
        exec("%s  = np.zeros((n_vis_data, trans_n_record))" % var)

###############################################
#            Create Socket                    #
###############################################
if tcp_trans == True:
    # connect socket
    socket_timeout = 2
    try:
        socket_con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_con.settimeout(socket_timeout)
        socket_con.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print 'Socket created'
    except:
        print 'fail to connect socket'
        if socket_con:
            socket_con.close()
            print 'Socket close'
        exit()

    try:
        socket_con.connect(( tcp_host, tcp_port))
    except:
        print 'socket connection error'
        exit()
        
    tcp_pack = bytearray(b'0'*1224)
    tcp_raw = bytearray(b'0'*1200)
    
###############################################
#            PostgreSQL connection            #
###############################################    
if sql_trans == True:
    import psycopg2
    try:
        psql_con = psycopg2.connect(
            user        = sql_username,
            password    = sql_password,
            host        = sql_host,
            port        = sql_port,
            database    = sql_database
        )
        cursor = psql_con.cursor()
    except (Exception, psycopg2.Error) as error :
        if(psql_con):
            print("Failed to connect postgres server", error)
    




    
    
    
    
    
    
    
def FetchingLoop():
    ######################################################
    #           The fetching loop starts                 #
    ######################################################
    global sample_time
    
    n_record = 0.0
    left_data = None

    # restart serial streaming
    SendCommand( ser_port, 'RS')
    # Drop out the first record
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

    sample_time = time.time()
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
                
                #print data_type, n_list,
                #for i in range(n_list):
                    #print len(raw_list[i]),
                #print ''
                
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
                            if left_data is None:
                                if n_bytes == 0:
                                    continue
                            # The case the buffer doesn't begin with "AT"
                            elif n_bytes + len(left_data) == RecordBytes:
                                record = True
                                raw_record = left_data + raw_list[i]
                                left_data = None
                        
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
                            
                            raw_record = raw_list[i]
                            n_bytes_accumulated = n_bytes
                            for shift_idx in range( i+1, n_list):
                                NBytes_next = len(raw_list[shift_idx])

                                if NBytes_next < RecordBytes:
                                    n_bytes_accumulated += 2 + NBytes_next
                                    raw_record = raw_record + b'AT' + raw_list[shift_idx]
                                    if n_bytes_accumulated == RecordBytes:
                                        record = True
                                        if shift_idx == n_list - 1:
                                            left_data = None
                                        break
                                    else:
                                        continue
                                else:
                                    print 'warning: length exceeded', NBytes_next
                                    break
                        
                                            
                        else: 
                            print 'warning'
                        
                    # The record fetched
                    if record == True:
                        # captured time
                        captured = time.time()
                        DT = datetime.datetime.fromtimestamp(captured)
                        
                        n_record += 1.0 / len(output_mode)
                        datatype    = raw_record[0]
                        serial_byte = raw_record[1]
                        
                        if data_type == 'Feature':
                            if datatype == str(b'\x31'):
                                pass
                            else:
                                print 'Feature code mismatched', datatype
                                
                            floats_byte = raw_record[2:126]
                            check_sum   = raw_record[126:130]
                            
                            if check_sum[0] != bytes_xor(floats_byte):
                                print('feature checksum is mismatched')
                                print check_sum, bytes_xor(floats_byte)
                            
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
                            
                            
                            if trans_adaptive:
                                if (x_std > trans_std_threshold) or \
                                   (y_std > trans_std_threshold) or \
                                   (z_std > trans_std_threshold):
                                    pass
                                elif (time.time() > sample_time):
                                    sample_time += trans_interval
                                else:
                                    continue
                            else: 
                                pass
                            
                            if csv2sftp_trans:
                                # capture time as CSV filename
                                csv_filename = sftp_tmp_dir + '/' + "fea_{0:0>4d}{1:0>2d}{2:0>2d}_{3:0>2d}{4:0>2d}{5:0>2d}.csv".format( DT.year, DT.month, DT.day, DT.hour, DT.minute, DT.second)
                                
                                # open CSV file
                                with open(csv_filename, 'w') as csvfile:
                                    # create CSV writer and write floating array
                                    writer = csv.writer(csvfile)
                                    writer.writerow(raw_float)
                                
                                if os.path.isfile(csv_filename):
                                    # upload CSV file 
                                    with srv.cd(csv2sftp_directory):
                                        srv.put(csv_filename) 
                                else:
                                    print csv_filename,'not found'

                                os.remove(csv_filename)
                                
                            if murano_trans:
                                headers = {
                                    'Content-Type': 'application/x-www-form-urlencoded',
                                    'X-Exosite-CIK': murano_CIK
                                }
                                
                                data = {"xmean"     :x_mean  ,
                                        "xstd"      :x_std   ,
                                        "xrms"      :x_rms   ,
                                        "xcf"       :x_crest ,
                                        "xskew"     :x_skew  ,
                                        "xkurtosis" :x_kurt  ,
                                        "xp2p"      :x_p2p   ,
                                        "ymean"     :y_mean  ,
                                        "ystd"      :y_std   ,
                                        "yrms"      :y_rms   ,
                                        "ycf"       :y_crest ,
                                        "yskew"     :y_skew  ,
                                        "ykurtosis" :y_kurt  ,
                                        "yp2p"      :y_p2p   ,
                                        "zmean"     :z_mean  ,
                                        "zstd"      :z_std   ,
                                        "zrms"      :z_rms   ,
                                        "zcf"       :z_crest ,
                                        "zskew"     :z_skew  ,
                                        "zkurtosis" :z_kurt  ,
                                        "zp2p"      :z_p2p   ,
                                        "temperature":temp    }

                                payload = {
                                    "data_in": json.dumps(data)
                                }

                                responce = requests.post(
                                    "https://"+murano_par.productid+".m2.exosite.io/onep:v1/stack/alias",
                                    headers = headers,
                                    data = payload
                                    )
                            
                            
                            if debug:
                                #print('{:12.4f} {:12.4f} {:12.4f}'.format(x_mean, y_mean, z_mean))
                                for i in range(n_vis_data):
                                    exec("array_firm[i, int(n_record)] = %s" % vis_datatype[i])
                            
                            
                        elif data_type == 'RAW':
                            assert(datatype == str(b'\x33'))
                            raw_sequence = raw_record[1] 
                            floats_byte = raw_record[2:1538]
                            check_sum = raw_record[1538:1542]
                            if check_sum[0] != bytes_xor(floats_byte):
                                framing_error = 1
                                print('raw checksum is mismatched')
                                #for i in range(4):
                                    #float_cs = floatbytes_xor(floats_byte)
                                    #bytes_cs = bytes_xor(floats_byte)
                                    #print ord(check_sum[i]), '\t', ord(float_cs[i]), '\t', ord(bytes_cs[0]) 
                            else:
                                framing_error = 0
                            
                            kernel_size = 128
                            
                            if tcp_trans == True:
                                captured_s  = int(captured)
                                captured_ms = int((captured - captured_s) * 1000)
                            
                                tcp_pack[0:4] = struct.pack('>L', captured_s) # unsigned long int (second)
                                tcp_pack[4:6] = struct.pack('>I', captured_ms)# unsigned int (mini-second)
                                tcp_pack[6:8] = struct.pack('>I', kernel_size)        # unsigned int (number of records)
                                tcp_pack[8]   = struct.pack('>B', framing_error) # framing error
                                #tcp_pack[9:23]=    ### reserved         
                                tcp_pack[23]  = check_sum[0]         
                                tcp_pack[24:1560]= floats_byte         
                                
                                socket_con.send(tcp_pack)
                            
                            if sql_trans:
                                cursor.execute(
                                    """ INSERT INTO raw (source, received, captured, err_frame, data_len, data) VALUES ('%s','%s','%s','%s','%s',%s)""" 
                                    % ('', DT, DT, str(framing_error),  kernel_size * 12, psycopg2.Binary(floats_byte))
                                )
                                psql_con.commit()
                                count = cursor.rowcount
                                print(n_record, "Record inserted successfully into raw table")
                                
                            if debug:
                                raw_float = struct.unpack( 'f'*384, floats_byte ) 
                                
                                for var in ['value', 'mean', 'std', 'rms', 'crest', 'skew', 'kurt',
                                            'variance', 'kurt2', 'std2',
                                            'maxi', 'mini', 'p2p', 'square', 'cube', 'diff', 'error']:
                                    # declare 3-elements vectors
                                    exec("%s = np.zeros(3)" % var)
                                    
                            
                                # skewness = E[(X-mu)^3] / (E([(X-mu)^2])^3/2
                                #          = (E[X^3] - 3 mu std^2 - mu^3) / std^3 
                                # ref: https://en.wikipedia.org/wiki/Skewness
                                
                                #
                                
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
                                        std2[j]     += diff[j] * diff[j]
                                        kurt2[j]     += pow(diff[j],4.0)
                                
                                for j in range(3):
                                    std2[j] = sqrt( std2[j] / kernel_size )
                                    kurt2[j] /= kernel_size * pow(std[j],4.0)
                                
                                
                                for feature in ['mean','std','rms','crest','skew','kurt','max','min','p2p']:
                                    for axis, ax_id in axis_dict.items():
                                        fea_var = axis+'_'+feature
                                        if feature == 'max' or feature == 'min':
                                            raw2fea_var = '%si[%d]' % (feature, ax_id)
                                        elif feature == 'std' or feature == 'kurt':
                                            raw2fea_var = '%s2[%d]' % (feature, ax_id)
                                        else:
                                            raw2fea_var = '%s[%d]' % (feature, ax_id)

                                        exec("fea_val = %s" % (fea_var))
                                        exec("raw2fea_val = %s" % (raw2fea_var))
                                        
                                        if raw2fea_val == 0.0:
                                            exec("error[%d] = %s - %s" % (ax_id, fea_var, raw2fea_var))
                                        else:
                                            exec("error[%d] = (%s - %s) / %s" % (ax_id, fea_var, raw2fea_var, raw2fea_var))

                                        
                                        #if abs(error[ax_id]) > 1e-2:
                                            #exec("print '%s',':',%e,'%s',':',%e" % (fea_var, fea_val, raw2fea_var, raw2fea_val))
                                        
                                        
                                        if isnan(error[j]):
                                            print 'Nan occurs at', axis, feature, fea_val, raw2fea_val
                                        
                                    #print('{:4s} diff: {:12.3e} {:12.3e} {:12.3e}'.format(feature, error[0], error[1], error[2]) )
                                
                                for i in range(n_vis_data):
                                    exec("array_num[i,int(n_record)-1] = %s[%d]" % ( vis_datatype[i][2:], axis_dict[vis_datatype[i][0]]) )
                                    if (vis_datatype[i][2:] == 'kurt') or (vis_datatype[i][2:] == 'std'): 
                                        exec("array_num2[i,int(n_record)-1] = %s2[%d]" % ( vis_datatype[i][2:], axis_dict[vis_datatype[i][0]]) )
                       
                        if float(int(n_record))  == n_record: 
                            print DT, 'received', int(n_record), 'records'
                    


        '''
        # stop while press "enter"
        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            line = raw_input()
            break
        '''
        # stop while reaching the number of fetching records
        if not trans_adaptive:
            if int(n_record) == trans_n_record:
                break

    # stop serial streaming
    SendCommand( ser_port, 'S')




#########################################
#       transmission interval loop      #
#########################################
# Continuous or adaptive sampling/monitoring
if (trans_interval == 0):
    FetchingLoop()
elif trans_adaptive:
    sample_time = time.time()
    FetchingLoop()
# Sampling within an interval (trans_interval)
else:
    sample_time = time.time()
    while True:
        if time.time() > sample_time:
            FetchingLoop()
            sample_time += trans_interval
        
        time.sleep(0.1)
        
        '''
        # stop while press "enter"
        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            line = raw_input()
            break
        '''
# Close serial port
ser_port.close()


#################################
#       Close Connection        #
#################################
# close socket connection
if tcp_trans:
    socket_con.close()

#closing database connection.
if sql_trans:
    cursor.close()
    psql_con.close()
    print("PostgreSQL connection is closed")

if csv2sftp_trans:
    # Closes the connection
    srv.close()


#############################
#   Debug Figures Output    #
#############################
if debug:
    import matplotlib.pyplot as plt
    Spec_figsize = (16, 12)
    Spec_dpi = 80
    
    for i in range(n_vis_data):
        fig, axes = plt.subplots(figsize=Spec_figsize, dpi=Spec_dpi)
        
        n_record_int = int(n_record)
        axes.plot(array_firm[i,:n_record_int], label='firmware', color='green', marker='o', linestyle='dashed', linewidth=2, markersize=12)
        axes.plot(array_num[i,:n_record_int], label='numerical' , color='blue', marker='D', linestyle='dashed', linewidth=2, markersize=12)
        if (vis_datatype[i][2:] == 'kurt') or (vis_datatype[i][2:] == 'std'):
            axes.plot(array_num2[i,:n_record_int], label='numerical2', color='red', marker='+', linestyle='dashed', linewidth=2, markersize=12)
            
            top_limit = 1.1 * np.max(array_firm[i,2:n_record_int])
            axes.set_ylim( top = top_limit, bottom = 0.0)
            #if vis_datatype[i][2:] == 'kurt':
                #axes.set_ylim( top = 2.0, bottom = 0.0)

                
        axes.set(xlabel='Record number', ylabel = vis_datatype[i], title='Time series of ' + vis_datatype[i])
        axes.legend()
        axes.grid(True)
        
        if 'save' in vis_output:
            filename = vis_datatype[i] + '_' + vis_lable + '.png'
            plt.savefig(filename)
    
    if 'show' in vis_output:
        plt.draw()
        plt.pause(1) # <-------
        raw_input("<Hit Enter To Close>")
        plt.close(fig)





