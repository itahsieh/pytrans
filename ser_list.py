#!/usr/bin/env python
from ser_conf import *
from MA_serial import ListConfig

ser_port = ser_config()
ListConfig(ser_port)
ser_port.close()
