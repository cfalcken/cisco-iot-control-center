#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
----------------------------------------------------------------------
 Send SMS to a device via REST API
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

__author__ = "Christian Falckenberg"
__email__ = "cfalcken@cisco.com"
__version__ = "1.0.0"
__copyright__ = "Copyright (c) 2023 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"

import json
import os
import argparse
import sys
import requests

# Import functions from parent directory
#
currdir = os.path.dirname(os.path.realpath(__file__))                       
sys.path.append(os.path.join(currdir, os.pardir))
import functions

# Parse the command line
parser = argparse.ArgumentParser(os.path.basename(__file__))
parser.add_argument("site", help="Name of the site as specified in settings.yaml", type=str)
parser.add_argument("iccid", help="Device ICCID", type=str)
parser.add_argument('-f', '--file', type=str, default='', help='File with content to send')
parser.add_argument('-t', '--text', type=str, default='Hello World', help='Text to send')
parser.add_argument("-d", "--debug", help="Enable debug output", action='store_true' )
args = parser.parse_args()

# Load settings for the site
#
settings = functions.load_site_settings(args.site)

# Build the fields selector in case it was provided
#
if args.file != '':
    with open(args.file, 'r') as file:
        text = file.read()
else:
    text = args.text

print("Sending SMS to ICCID:", args.iccid, file=sys.stderr)
print(text, file=sys.stderr)

# Send the API request
#
myResponse = requests.post(
        settings["resturl"] + "/devices/" + args.iccid + "/smsMessages/",
        auth=(settings["username"],settings["apikey"]),
        json={"messageText": text})

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