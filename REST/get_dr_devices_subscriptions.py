#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
----------------------------------------------------------------------
 Get list of device subscriptions using Dynamic Reporting via REST API
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
from time import strftime, localtime

# Import functions from parent directory
#
currdir = os.path.dirname(os.path.realpath(__file__))                       
sys.path.append(os.path.join(currdir, os.pardir))
import functions

# Parse the command line to get the site name
# Optionally, specify an account ID and a modification date
#
parser = argparse.ArgumentParser(os.path.basename(__file__))
parser.add_argument("site", help="Name of the site as specified in settings.yaml", type=str)
parser.add_argument("-a", "--account", default='', help="ID of the account", type=str)
parser.add_argument("-s", "--startdate", type=str, help='Start date (YYYYMMDD)')
parser.add_argument("-e", "--enddate", type=str, help='End date (YYYYMMDD)')
parser.add_argument("-b", "--billingcycle", type=str, help='Billing cycle (YYYYMM)')
parser.add_argument("-d", "--debug", help="Enable debug output", action='store_true' )
args = parser.parse_args()

# Load settings for the site
#
settings = functions.load_site_settings(args.site)

devices=[]
page = 1
lastpage = False

if args.billingcycle:
    params={
        "page_number": page,
        "billing_cycle": args.billingcycle
    }
elif args.startdate and args.enddate:
    params={
        "page_number": page,
        "start_date": args.startdate,
        "end_date": args.enddate
    }
else:
    sys.exit (f"Provide either billing cycle or start and end date")

url = settings["resturl"] + "/dynareport/operators/" + str(settings["operator"])

if "account" in settings:
    url +=  "/accts/" + str(settings["account"])
elif args.account:
    url += "/accts/" + str(args.account)

url += "/device/subscriptions"

while not lastpage:

    print(f"Requesting page {page}", file=sys.stderr)

    params["page_number"] = page

    jData = json.loads(functions.get_data(
        url,
        settings["username"], 
        settings["apikey"], 
        params, 
        debug=args.debug))
    
    try:
        for device in jData["body"]["data"]:
            device["period_ending_str"] = strftime('%Y-%m-%d', localtime(device["period_ending"]/1000))
            devices.append(device) 
    except:
        sys.exit(jData)
    page+=1
    lastpage = page > jData["body"]["meta"]["total_page"]

# Dump the result
#
print(json.dumps(devices, indent=4))
