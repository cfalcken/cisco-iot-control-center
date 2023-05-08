#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
----------------------------------------------------------------------
 Get device usage via REST API
----------------------------------------------------------------------

Copyright (c) 2023 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.

"""

import requests 
import json 
import yaml
import os
from pathlib import Path
import argparse
import sys

__author__ = "Christian Falckenberg"
__email__ = "cfalcken@cisco.com"
__version__ = "1.0.0"
__copyright__ = "Copyright (c) 2023 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"

# Parse the command line to get the site name and ICCID
# Optionally, specify fields to print only a partial response
#
parser = argparse.ArgumentParser(os.path.basename(__file__))
parser.add_argument("site", help="Name of the site as specified in settings.yaml", type=str)
parser.add_argument("iccid", help="Device ICCID", type=str)
parser.add_argument('-f', '--fields', type=str, default='', help='Fields to print from JSON')
args = parser.parse_args()

# Build the fields selector in case it was provided
#
fields =''
if args.fields != '':
    fields = '?fields=' + args.fields

# Get the settings (URL, username, apikey) from external file
#
full_file_path = Path(__file__).parent.joinpath('../settings.yaml')
with open(full_file_path) as settings:
    settings = yaml.load(settings, Loader=yaml.Loader)

print("Getting usages for ICCID", args.iccid, file=sys.stderr)

# Send the API request
#
myResponse = requests.get(
        settings[args.site]["resturl"] + "/devices/" + args.iccid + "/ctdUsages" + fields,
        auth=((settings[args.site]["username"]),settings[args.site]["apikey"]))
                      
# For successful API call, response code will be 200 (OK)
#
if(myResponse.ok):
    
    # Loading the response data into a dict variable
    jData = json.loads(myResponse.content)

    # print to stdout
    json.dump(jData,sys.stdout, indent=4)

else:
    # If response code is not ok (200), print the resulting http error code with description
    print("Failure")
    myResponse.raise_for_status()

print()