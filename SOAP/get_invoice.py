#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
----------------------------------------------------------------------
Get invoice via SOAP API
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
parser.add_argument("startdate", help="Cycle start date, e.g. 2023-01-01", type=str)
parser.add_argument("-a", "--account", help="ID of the account", type=str, action='append')
parser.add_argument("-f", "--accountfile", help="File with account IDs", type=str)
args = parser.parse_args()

# Get the list of account IDs
#
if args.account == None:
    if args.accountfile == None:
        print("Provide either one or more account IDs with option -a or use -f for a filename with account IDs")
        exit()
    else:
        with open(args.accountfile) as accfile:
            accounts = accfile.read().splitlines()
else:
    accounts = args.account

# Load settings for the site
#
settings = functions.load_site_settings(args.site)

url         = settings["wsdlurl"] + '/Billing.wsdl'
soap_action = 'http://api.jasperwireless.com/ws/service/billing/GetInvoice'
messageId   = '123456'
version     = '1'

# Create a SOAP client
#
client = Client(url, wsse=UsernameToken(settings["username"], settings["password"]))

# Set SOAP action in the header
#
client.transport.session.headers['SOAPAction'] = soap_action

# Call the GetInvoice method
#
allinvoices=[]

for account in accounts:

    print("Getting invoice for account ID", account, file=sys.stderr)

    try:
        result = client.service.GetInvoice(
            messageId=messageId,
            version=version,
            licenseKey=settings["licensekey"],
            accountId=account,
            cycleStartDate=args.startdate,
        )

        # Collect the result
        #
        allinvoices.append(functions.convert_zeep_object(result))
        
    except zeep.exceptions.Fault as fault:
        print("Error", fault.message, ":", SoapError(fault.message))

# print to stdout
json.dump(allinvoices,sys.stdout, indent=4)
