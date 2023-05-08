#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
----------------------------------------------------------------------
Get device details via SOAP API
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

import argparse
from pathlib import Path
import sys
import os
import logging
import yaml
import zeep
from zeep import Client
from zeep.wsse.username import UsernameToken
from errors import SoapError

__author__ = "Christian Falckenberg"
__email__ = "cfalcken@cisco.com"
__version__ = "1.0.0"
__copyright__ = "Copyright (c) 2023 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"


logging.basicConfig(level=logging.INFO)
logging.getLogger('zeep').setLevel(logging.ERROR)

# Parse the command line to get the site name
# Optionally, specify an account ID and a modification date
#
parser = argparse.ArgumentParser(os.path.basename(__file__))
parser.add_argument("site", help="Name of the site as specified in settings.yaml", type=str)
parser.add_argument("-a", "--account", default='', help="ID of the account", type=str)
parser.add_argument("-m", "--modified", default='2000-01-01T00:00:00+00:00', help="Modified since, e.g. 2000-01-01T00:00:00+00:00", type=str)
args = parser.parse_args()

# Get the settings (URL, username, apikey) from external file
#
full_file_path = Path(__file__).parent.joinpath('../settings.yaml')
with open(full_file_path) as settings:
    settings = yaml.load(settings, Loader=yaml.Loader)


url         = settings[args.site]["wsdlurl"] + '/Terminal.wsdl'
soap_action = 'http://api.jasperwireless.com/ws/service/terminal/GetTerminalDetails'
messageId   = '123456'
version     = '1'

# Create a SOAP client
#
client = Client(url, wsse=UsernameToken(settings[args.site]["username"], settings[args.site]["password"]))

# Set SOAP action in the header
#
client.transport.session.headers['SOAPAction'] = soap_action

page = 1
count = 0
totalPages = 100

print("Getting all devices", file=sys.stderr)

while page < totalPages:

    # Call the GetTerminalDetails method
    #
    try:
        if args.account == "":
            result = client.service.GetModifiedTerminals(
                messageId=messageId, 
                version=version, 
                licenseKey=settings[args.site]["licensekey"],
                since=args.modified,
                pageNumber=page
            )
        else:
            result = client.service.GetModifiedTerminals(
                messageId=messageId, 
                version=version, 
                licenseKey=settings[args.site]["licensekey"],
                accountId=args.account,
                since=args.modified,
                pageNumber=page
        )

    except zeep.exceptions.Fault as fault:
        print("Error", fault.message, ":", SoapError(fault.message))
        break

    for iccid in result.iccids["iccid"]:
        print (iccid)

    totalPages = result.totalPages
    page += 1
    if page < totalPages:
        print(f"Requesting page {page} of {totalPages}", file=sys.stderr)
