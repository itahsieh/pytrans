import sys
import serial
import time

sys.path.append('/home/vandine/MachineAnalyzer/lib')
from MA_utilities import *

def SerialConnect( Port, BaudRate):
    try:
        ser = serial.Serial(
            port = Port, 
            baudrate = BaudRate, 
            bytesize = serial.EIGHTBITS,
            parity = serial.PARITY_NONE,
            stopbits = serial.STOPBITS_ONE,
            timeout = 1
            )
        return ser
    except:
        sys.exit("Error connecting device")

def SendCommand( ser_port, string):
    AT_string = 'AT$' + string + '\r'
    ser_port.write(AT_string.encode() )
    time.sleep(0.1)
    ser_port.flush()
    
    
def ListConfig(ser_port):
    SendCommand( ser_port, 'S')
    SendCommand( ser_port, 'LIST')
    ser_port.flush()
    while ser_port.inWaiting() > 0:
        response = ser_port.readlines()
        print(
            bcolors.WARNING +
            'LIST the configuration of the sensor' +
            bcolors.ENDC
            )
        #print(response)
        
        for i in range(len(response)):
            line = response[i].strip().decode('charmap')
            print(line)
        
        
