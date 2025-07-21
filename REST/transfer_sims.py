#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
----------------------------------------------------------------------
 Transfer SIMs to new account
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
import csv

# Import functions from parent directory
#
currdir = os.path.dirname(os.path.realpath(__file__))                       
sys.path.append(os.path.join(currdir, os.pardir))
import functions

# Parse the command line
parser = argparse.ArgumentParser(os.path.basename(__file__))
parser.add_argument("site", help="Name of the site as specified in settings.yaml", type=str)
parser.add_argument("account", help="Account ID of the target account", type=str)
parser.add_argument("-i", "--iccid", help="Device ICCID", type=str, action='append')
parser.add_argument("-f", "--file", help="File with ICCIDs (with at least one CSV column with header 'ICCID')", type=str)
parser.add_argument("-r", "--rateplan", help="Optional target rate plan name", type=str)
parser.add_argument("-c", "--commplan", help="Optional target comm plan name", type=str)
parser.add_argument("-s", "--state", help="Optional target SIM state", type=str)
parser.add_argument("-u", "--url", help="Optional call back URL", type=str)
parser.add_argument("-d", "--debug", help="Enable debug output", action='store_true' )
args = parser.parse_args()

# Get the list of ICCIDs
#
if args.iccid == None:
    if args.file == None:
        print("Provide either one or more ICCIDs with option -i or use -f for a filename with ICCIDs")
        exit()
    else:
        params ={}
        iccids = []
        with open(args.file, mode='r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                iccid = row.pop('ICCID')
                iccids.append(iccid)
                params[iccid] = row
else:
    iccids = args.iccid

# Load settings for the site
#
settings = functions.load_site_settings(args.site)

# Build parameter
#
params = {}
params["accountId"] = args.account
params["iccids"] = iccids
if args.rateplan:
    params["ratePlanName"] = args.rateplan
if args.commplan:
    params["commPlanName"] = args.commplan
if args.state:
    params["simState"] = args.state
if args.url:
    params["callbackUrl"] = args.url

# Send the API request
#
jData = json.loads(functions.get_data(
    settings["resturl"] + "/devices/transferDeviceToAccount",
    settings["username"],
    settings["apikey"],
    method="post",
    jsondata=params,
    debug=args.debug)
)

json.dump(jData,sys.stdout, indent=4)

print()

