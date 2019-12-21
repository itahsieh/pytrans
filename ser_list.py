#!/usr/bin/env python
from ser_conf import *
from MA_serial import ListConfig

ser_port = ser_config(115200)
if ser_port != -1:
    ListConfig(ser_port)
    ser_port.close()
