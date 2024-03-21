#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
----------------------------------------------------------------------
Get usage details via SOAP API
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

import argparse
import sys
import os
import logging
import zeep
import json
import datetime
from zeep import Client
from zeep.wsse.username import UsernameToken
from errors import SoapError

# Import functions from parent directory
#
currdir = os.path.dirname(os.path.realpath(__file__))                       
sys.path.append(os.path.join(currdir, os.pardir))
import functions

logging.basicConfig(level=logging.INFO)
logging.getLogger('zeep').setLevel(logging.ERROR)

# Parse the command line
#
parser = argparse.ArgumentParser(os.path.basename(__file__))
parser.add_argument("site", help="Name of the site as specified in settings.yaml", type=str)
parser.add_argument("iccid", help="Device ICCID", type=str)
parser.add_argument("startdate", help="Cycle start date, e.g. 2023-01-01", type=str)
args = parser.parse_args()

# Load settings for the site
#
settings = functions.load_site_settings(args.site)

url = settings["wsdlurl"] + '/Billing.wsdl'
soap_action = 'http://api.jasperwireless.com/ws/service/billing/GetTerminalUsageDataDetails'
messageId = '123456'
version = '1'

# Create a SOAP client
#
client = Client(url, wsse=UsernameToken(settings["username"], settings["password"]))

# Set SOAP action in the header
#
client.transport.session.headers['SOAPAction'] = soap_action

allrecs = []
reccount = 0
totalduration = 0
totalvolume = 0

page = 1
totalPages = 100

print("Getting all records for the device ICCID", args.iccid, file=sys.stderr)

while page <= totalPages:

    # Call the SOAP method
    #
    try:
        result = client.service.GetTerminalUsageDataDetails(
            messageId=messageId,
            version=version,
            licenseKey=settings["licensekey"],
            iccid=args.iccid,
            cycleStartDate=args.startdate,
            pageNumber=page)

        # Process each record that is returned and
        # extract summarize duration and volume for each session
        # (which is identified by records having the same sessionStartTime)
        #
        for record in result.usageDetails["usageDetail"]:
            volume = int(record["dataVolume"].to_integral())
            duration = record["duration"]
            starttime = record["sessionStartTime"].isoformat()
            epoch = int(record["sessionStartTime"].timestamp())

            totalduration += duration
            totalvolume += volume
            reccount += 1

            recout = {}
            recout["volume"] = volume
            recout["duration"] = duration
            recout["starttime_iso"] = starttime
            recout["starttime_epoch"] = epoch
            allrecs.append(recout)

        totalPages = result.totalPages
        page += 1
        if page <= totalPages:
            print(f"Requesting page {page} of {totalPages}", file=sys.stderr)

    except zeep.exceptions.Fault as fault:
        print("Error", fault.message, ":", SoapError(fault.message))
        break

if allrecs != []:

    sorted_allrecs = sorted(allrecs, key=lambda d: d['starttime_epoch'])
    print(json.dumps(sorted_allrecs, indent=4))

    # Print a summary of the records
    #
    print(f"Counted {str(reccount)} record(s) with a total duration of {datetime.timedelta(seconds = totalduration)} hours and a volume of {str(totalvolume)} KB", file=sys.stderr)
