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
import json
from zeep import Client, helpers
from zeep.wsse.username import UsernameToken
from errors import SoapError

__author__ = "Christian Falckenberg"
__email__ = "cfalcken@cisco.com"
__version__ = "1.0.0"
__copyright__ = "Copyright (c) 2023 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"

# Function to convert the object returned by the SOAP call to readable JSON
# (may be called recursively)
#
def convert_zeep_object(obj):
    items={}
    for key in obj:
        if isinstance(zeep.helpers.serialize_object(obj[key]),dict):
            items[key]=convert_zeep_object(obj[key])
        else:
            items[key] = str(obj[key])
    return items

# Enable logging
#
logging.basicConfig(level=logging.INFO)
logging.getLogger('zeep').setLevel(logging.ERROR)

# Parse the command line to get the site name and ICCID
#
parser = argparse.ArgumentParser(os.path.basename(__file__))
parser.add_argument("site", help="Name of the site as specified in settings.yaml", type=str)
parser.add_argument("-i", "--iccid", help="Device ICCID", type=str, action='append')
parser.add_argument("-f", "--iccidfile", help="File with ICCIDs", type=str)
args = parser.parse_args()

# Get the settings (URL, username, apikey) from external file
#
full_file_path = Path(__file__).parent.joinpath('../settings.yaml')
with open(full_file_path) as settings:
    settings = yaml.load(settings, Loader=yaml.Loader)

print("Getting details for ICCID", args.iccid, file=sys.stderr)

url = settings[args.site]["wsdlurl"] + '/Terminal.wsdl'
soap_action = 'http://api.jasperwireless.com/ws/service/terminal/GetTerminalDetails'
messageId = '123456'
version = '1'

# Get the list of ICCIDs
#
if args.iccid == None:
    if args.iccidfile == None:
        print("Provide either one or more ICCIDs with option -i or use -f for a filename with ICCIDs")
        exit()
    else:
        with open(args.iccidfile) as iccidfile:
            iccids = iccidfile.read().splitlines()
else:
    iccids = args.iccid

# Create a SOAP client
#
client = Client(url, wsse=UsernameToken(
    settings[args.site]["username"], settings[args.site]["password"]))

# Set SOAP action in the header
#
client.transport.session.headers['SOAPAction'] = soap_action

alldevices=[]
# Use a loop in case a large list of ICCDIs is given
#
for i in range(0, len(iccids), 50):
    iccid_slice = iccids[i:i + 50]

    # Call the GetTerminalDetails method
    #
    try:
        result = client.service.GetTerminalDetails(
            messageId=messageId,
            version=version,
            licenseKey=settings[args.site]["licensekey"],
            iccids={"iccid": iccid_slice}
         )

        # Convert the result
        # 
        for record in result.terminals["terminal"]:
            terminal = convert_zeep_object(record)  
            alldevices.append(terminal)

    except zeep.exceptions.Fault as fault:
        print("Error", fault.message, ":", SoapError(fault.message), file=sys.stderr)

# print to stdout
json.dump(alldevices,sys.stdout, indent=4)
