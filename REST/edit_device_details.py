#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
----------------------------------------------------------------------
 Edit device details via REST API
---------------------------------------------------------------------

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

import requests 
import json
import os
import argparse
import sys

# Import functions from parent directory
#
currdir = os.path.dirname(os.path.realpath(__file__))                       
sys.path.append(os.path.join(currdir, os.pardir))
import functions

# Parse the command line
#
parser = argparse.ArgumentParser(os.path.basename(__file__))
parser.add_argument("site", help="Name of the site as specified in settings.yaml", type=str)
parser.add_argument("-i", "--iccid", help="Device ICCID", type=str, action="append")
parser.add_argument("-l", "--list", help="File with ICCIDs", type=str)
parser.add_argument("-p", "--param", type=str, default="", help="Parameters to modify in JSON format")
parser.add_argument("-d", "--debug", help="Enable debug output", action='store_true' )
args = parser.parse_args()

# Get the list of ICCIDs
#
if args.iccid == None:
    if args.list == None:
        print("Provide either one or more ICCIDs with option -i or use -l for a filename with ICCIDs")
        exit()
    else:
        with open(args.list) as iccidfile:
            iccids = iccidfile.read().splitlines()
else:
    iccids = args.iccid

# Load settings for the site
#
settings = functions.load_site_settings(args.site)


alldevices=[]
print(f"Processing {len(iccids)} ICCIDs", file=sys.stderr)
for iccid in iccids:

    print("Editing parameters for ICCID", iccid, file=sys.stderr)

    # Send the API request
    #
    myResponse = requests.put(
        settings["resturl"] + "/devices/" + iccid,
        auth=((settings["username"]),settings["apikey"]),
        json=json.loads(args.param)
        )

    if(myResponse.ok):
        print ("Update successful")
    else:
        print("Failure")
        myResponse.raise_for_status()

    jData = json.loads(myResponse.content)
    json.dump(jData,sys.stdout, indent=4)

    print()

