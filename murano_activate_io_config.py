#!/usr/bin/env python

import requests
import json

import os
import sys
import time
import datetime
import random

from murano_par import *


host_address_base = os.getenv('SIMULATOR_HOST', 'm2.exosite.io')
host_address = 'https://' + productid + '.' + host_address_base
token_filename = productid + "_" + identifier + "_cik"

# Activate
try:
    # print("attempt to activate on Murano")

    url = host_address + '/provision/activate'
    headers = {'Content-Type':'application/x-www-form-urlencoded; charset=utf-8'}
    payload = 'id=' + identifier

    response = requests.post(url, data=payload, headers=headers)
    print 'http status:', response.status_code
    print 'token:', response.text


    # HANDLE POSSIBLE RESPONSES
    if response.status_code == 200:
        new_cik = response.text
        print("Activation Response: New CIK: {} ..............................".format(new_cik[0:10]))
        
        print("storing CIK to flie")
        f = open(token_filename, "w")  # opens file that stores CIK
        f.write(new_cik)
        f.close()
    elif response.status_code == 409:
        print("Activation Response: Device Aleady Activated, there is no new CIK")
    elif response.status_code == 404:
        print("Activation Response: Device Identity ({}) activation not available or check Product Id ({})".format(
            identifier,
            productid
            ))
    else:
        print("Activation Response: failed request: {} {}".format(str(response.status_code), response.text))

except Exception as e:
    # pass
    print("Exception: {}".format(e))

# io_config


config_json =  {
    "last_edited":"2019-11-13T09:48:57+00:00",
    "channels":{
        "xmean":{"display_name":"x mean",
                 "properties":{"data_unit":"mg","precision":2,"data_type":"NUMBER"}},
        "xstd":{"display_name":"x std",
                "properties":{"data_unit":"mg","precision":2,"data_type":"NUMBER"}},
        "xrms":{"display_name":"x rms",
                "properties":{"data_unit":"mg","precision":2,"data_type":"NUMBER"}},
        "xcf":{"display_name":"x crestf",
               "properties":{"data_unit":"","precision":2,"data_type":"NUMBER"}},
        "xskew":{"display_name":"x skew",
                 "properties":{"data_unit":"","precision":2,"data_type":"NUMBER"}},
        "xkurtosis":{"display_name":"x kurtosis",
                     "properties":{"data_unit":"","precision":2,"data_type":"NUMBER"}},
        "xmax":{"display_name":"x max",
                "properties":{"data_unit":"mg","precision":2,"data_type":"NUMBER"}},
        "xmin":{"display_name":"x min",
                "properties":{"data_unit":"mg","precision":2,"data_type":"NUMBER"}},
        "xp2p":{"display_name":"x p2p",
                "properties":{"data_unit":"mg","precision":2,"data_type":"NUMBER"}},
        "xspeed":{"display_name":"x speed",
                  "properties":{"data_unit":"","precision":2,"data_type":"NUMBER"}},
        
        "ymean":{"display_name":"y mean",
                 "properties":{"data_unit":"mg","precision":2,"data_type":"NUMBER"}},
        "ystd":{"display_name":"y std",
                "properties":{"data_unit":"mg","precision":2,"data_type":"NUMBER"}},
        "yrms":{"display_name":"y rms",
                "properties":{"data_unit":"mg","precision":2,"data_type":"NUMBER"}},
        "ycf":{"display_name":"y crestf",
               "properties":{"data_unit":"","precision":2,"data_type":"NUMBER"}},
        "yskew":{"display_name":"y skew",
            "properties":{"data_unit":"","precision":2,"data_type":"NUMBER"}},
        "ykurtosis":{"display_name":"y kurtosis",
                "properties":{"data_unit":"","precision":2,"data_type":"NUMBER"}},
        "ymax":{"display_name":"y max",
                "properties":{"data_unit":"mg","precision":2,"data_type":"NUMBER"}},
        "ymin":{"display_name":"y min",
                "properties":{"data_unit":"mg","precision":2,"data_type":"NUMBER"}},
        "yp2p":{"display_name":"y p2p",
                "properties":{"data_unit":"mg","precision":2,"data_type":"NUMBER"}},
        "yspeed":{"display_name":"y speed",
                  "properties":{"data_unit":"","precision":2,"data_type":"NUMBER"}},
        
        "zmean":{"display_name":"z mean",
                 "properties":{"data_unit":"mg","precision":2,"data_type":"NUMBER"}},
        "zstd":{"display_name":"z std",
                "properties":{"data_unit":"mg","precision":2,"data_type":"NUMBER"}},
        "zrms":{"display_name":"z rms",
                "properties":{"data_unit":"mg","precision":2,"data_type":"NUMBER"}},
        "zcf":{"display_name":"z crestf",
               "properties":{"data_unit":"","precision":2,"data_type":"NUMBER"}},
        "zskew":{"display_name":"z skew",
                 "properties":{"data_unit":"","precision":2,"data_type":"NUMBER"}},
        "zkurtosis":{"display_name":"z kurtosis",
                     "properties":{"data_unit":"","precision":2,"data_type":"NUMBER"}},
        "zmax":{"display_name":"z max",
                "properties":{"data_unit":"mg","precision":2,"data_type":"NUMBER"}},
        "zmin":{"display_name":"z min",
                "properties":{"data_unit":"mg","precision":2,"data_type":"NUMBER"}},
        "zp2p":{"display_name":"z p2p",
                "properties":{"data_unit":"mg","precision":2,"data_type":"NUMBER"}},
        "zspeed":{"display_name":"z speed",
                  "properties":{"data_unit":"","precision":2,"data_type":"NUMBER"}},
        
        "temperature":{"display_name":"temperature",
                       "properties":{"data_unit":"degree C","precision":2,"data_type":"NUMBER"}}}
        }


try:
    f = open(token_filename, "r+")  # opens file to store CIK
    local_cik = f.read()
    f.close()
except Exception as e:
    print("Unable to read a stored CIK: {}".format(e))

headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'X-Exosite-CIK': local_cik
}
payload = {
    "config_io": json.dumps(config_json)
}

r = requests.post(
    "https://"+productid+".m2.exosite.io/onep:v1/stack/alias",
    headers = headers,
    data = payload
    )
