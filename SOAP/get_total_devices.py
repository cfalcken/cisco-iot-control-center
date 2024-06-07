#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
----------------------------------------------------------------------
Get total number of devices via SOAP API
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
parser.add_argument("-a", "--account", help="ID of the account", type=str, action='append')
parser.add_argument("-f", "--accountfile", help="File with account IDs", type=str)
parser.add_argument("-m", "--modified", default='2000-01-01T00:00:00+00:00', help="Modified since, e.g. 2000-01-01T00:00:00+00:00", type=str)
parser.add_argument("-s", "--state", default='', help="SIM state", type=str)
args = parser.parse_args()

# Get the list of account IDs
#
if args.account == None:
    if args.accountfile == None:
        accounts = ["All"]
    else:
        with open(args.accountfile) as accfile:
            accounts = accfile.read().splitlines()
else:
    accounts = args.account

# Load settings for the site
#
settings = functions.load_site_settings(args.site)

url         = settings["wsdlurl"] + '/Terminal.wsdl'
soap_action = 'http://api.jasperwireless.com/ws/service/terminal/GetTerminalDetails'
messageId   = '123456'
version     = '1'

# Create a SOAP client
#
client = Client(url, wsse=UsernameToken(settings["username"], settings["password"]))

# Set SOAP action in the header
#
client.transport.session.headers['SOAPAction'] = soap_action

page = 1
count = 0
totalPages = 100

if args.state !="":
    state = args.state
else:
    state ="UNKNOWN"

allinvoices=[]

for account in accounts:

    print(f"Getting device totals for account ID {account}", file=sys.stderr)

    # Call the GetTerminalDetails method
    #
    print("Requesting devices from first page", file=sys.stderr)

    try:
        if account == "All":
            result = client.service.GetModifiedTerminals(
                messageId=messageId, 
                version=version, 
                licenseKey=settings["licensekey"],
                since=args.modified,
                simState=state,
                pageNumber=1
            )
        else:
            result = client.service.GetModifiedTerminals(
                messageId=messageId, 
                version=version, 
                licenseKey=settings["licensekey"],
                accountId=account,
                since=args.modified,
                simState=state,
                pageNumber=1
            )

    except zeep.exceptions.Fault as fault:
        print("Error", fault.message, ":", SoapError(fault.message))

    devices = len(result.iccids["iccid"])
    totalPages = result.totalPages

    # Repeat the request for the last page if there are more
    #
    if totalPages > 100:
        print(f"Found more than hundred pages ({totalPages})", file=sys.stderr)
        print(f"Estimating number of devices by rounding up to full pages", file=sys.stderr)

        print (f"{account},{devices*totalPages}")

    elif totalPages >0:

        print(f"Found {totalPages} pages; requesting devices from last page", file=sys.stderr)
 
        try:
            if account == "All":
                result = client.service.GetModifiedTerminals(
                    messageId=messageId, 
                    version=version, 
                    licenseKey=settings["licensekey"],
                    since=args.modified,
                    simState=state,
                    pageNumber=totalPages
                )
            else:
                result = client.service.GetModifiedTerminals(
                    messageId=messageId, 
                    version=version, 
                    licenseKey=settings["licensekey"],
                    accountId=account,
                    since=args.modified,
                    simState=state,
                    pageNumber=totalPages
            )
        except zeep.exceptions.Fault as fault:
            print("Error", fault.message, ":", SoapError(fault.message))

        print (f"{account},{devices*(totalPages-1)+len(result.iccids['iccid'])}")

    else:
        print (f"{account},{devices}")
