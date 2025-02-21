#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
----------------------------------------------------------------------
 Get aggregated usage using Dynamic Reporting via REST API
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
import datetime

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
parser.add_argument("-g", "--groupby", type=str, help='One or more of carrier,country,rate plan,rating zone, separated by comma')
parser.add_argument("-m", "--metrics", type=str, help='Usage metric (one or more of data,voice,sms,vmo,vmt,smo,smt, separated by comma')
parser.add_argument("-d", "--debug", help="Enable debug output", action='store_true' )
args = parser.parse_args()

# Load settings for the site
#
settings = functions.load_site_settings(args.site)

records=[]
page = 1
lastpage = False

if args.metrics:
    metrics = args.metrics
else:
    metrics = "data,voice,sms,vmo,vmt,smo,smt"

if args.billingcycle:
    params={
        "page_number": page,
        "metrics": metrics,
        "billing_cycle": args.billingcycle
    }
elif args.startdate and args.enddate:
    params={
        "page_number": page,
        "metrics": metrics,
        "start_date": args.startdate,
        "end_date": args.enddate
    }
else:
    sys.exit (f"Provide either billing cycle or start and end date")

if args.groupby:
    params["group_by"] = args.groupby

url = settings["resturl"] + "/dynareport/operators/" + str(settings["operator"])

if "account" in settings:
    url +=  "/accts/" + str(settings["account"])
elif args.account:
    url += "/accts/" + str(args.account)

url += "/usage"

while not lastpage:

    print(f"{datetime.datetime.now()}: Requesting page {page}", file=sys.stderr)

    params["page_number"] = page

    jData = json.loads(functions.get_data(
        url,
        settings["username"], 
        settings["apikey"], 
        params, 
        debug=args.debug))
    
    print(f"{datetime.datetime.now()}: Response received", file=sys.stderr)

    try:
        for record in jData["body"]["data"]:
            for element in record["group_elements"]:
                record[element["key"]] = element["value"]
            record.pop("group_elements",None)

            for element in record["metric_data"]:
                record[element["metricType"]+"_usage"] = element["usage"]
                record[element["metricType"]+"_count"] = element["count"]
            record.pop("metric_data",None)

            records.append(record)


    except Exception as e:
        print (e)
        sys.exit(json.dumps(jData, indent=4))
    page+=1
    lastpage = page > jData["body"]["metaData"]["total_pages"]

# Dump the result
#
print(json.dumps(records, indent=4))
