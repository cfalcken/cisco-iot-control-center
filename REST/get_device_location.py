#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
----------------------------------------------------------------------
 Get device location history via REST API
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

# Import functions from parent directory
#
currdir = os.path.dirname(os.path.realpath(__file__))                       
sys.path.append(os.path.join(currdir, os.pardir))
import functions

# Parse the command line
#
parser = argparse.ArgumentParser(os.path.basename(__file__))
parser.add_argument("site", help="Name of the site as specified in settings.yaml", type=str)
parser.add_argument("-i", "--iccid", help="Device ICCID", type=str, action='append')
parser.add_argument("-l", "--list", help="File with ICCIDs", type=str)
parser.add_argument("-f", "--fromDate", type=str, help='Location history from yyyy-MM-ddTHH:mm:ssZ')
parser.add_argument("-t", "--toDate", type=str, help='Location history until yyyy-MM-ddTHH:mm:ssZ')
parser.add_argument("-g", "--google", help="Use Google's geolocation API", action='store_true' )
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
if args.google:
    google_settings = functions.load_site_settings("google")

alldetails=[]
params={}

print(f"Getting location history for {len(iccids)} ICCIDs", file=sys.stderr)
if args.fromDate != None:
    print("  from ", args.fromDate, file=sys.stderr)
    params["fromDate"] = args.fromDate
if args.toDate != None:
    print("  until ", args.toDate, file=sys.stderr)
    params["toDate"] = args.toDate

locations=[]

for iccid in iccids:

    print("ICCID: ", iccid, file=sys.stderr)

    page = 1
    lastpage = False

    while not lastpage:

        print(f"  Requesting page {page}", file=sys.stderr)

        params["pageNumber"] = page

        jData = json.loads(functions.get_data(
            settings["resturl"] + "/devices/" + iccid + "/locationHistory",
            settings["username"], 
            settings["apikey"], 
            params, 
            debug=args.debug))
        
        for location in jData["simLocations"]:
            locations.append(location)

        page+=1
        lastpage = jData["lastPage"]

# Enrich the locations with data from Google's geolocation API
#
if args.google:
    for location in locations:
        cell={}
        cell["cellId"]            = location["cellId"]
        cell["locationAreaCode"]  = location["cellLac"]
        cell["mobileCountryCode"] = location["servingMcc"]
        cell["mobileNetworkCode"] = location["servingMnc"]
        celllist=[]
        celllist.append(cell)
        jsondata = {"cellTowers": celllist}

        jGoogleData = json.loads(functions.get_data(
            google_settings["resturl"] + "/geolocate",
            '',
            '',
            {"key": google_settings["apikey"]},
            method="post",
            jsondata=jsondata,
            debug=args.debug))
        
        location["google_latitude"] = jGoogleData["location"]["lat"]
        location["google_longitude"] = jGoogleData["location"]["lng"]

print(json.dumps(locations, indent=4))
