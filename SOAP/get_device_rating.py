#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
----------------------------------------------------------------------
Get device rating via SOAP API
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

# Load settings for the site
#
settings = functions.load_site_settings(args.site)

url         = settings["wsdlurl"] + '/Terminal.wsdl'
soap_action = 'http://api.jasperwireless.com/ws/service/terminal/GetTerminalRating'
messageId   = '123456'
version     = '1'

# Create a SOAP client
#
client = Client(url, wsse=UsernameToken(settings["username"], settings["password"]))

# Set SOAP action in the header
#
client.transport.session.headers['SOAPAction'] = soap_action

# Call the GetTerminalDetails method
#
alldevices=[]

for iccid in iccids:
    try:
        result = client.service.GetTerminalRating(
            messageId=messageId,
            version=version,
            licenseKey=settings["licensekey"],
            iccid=iccid
        )

        # Collect the result
        # 
        if result.terminalRatings != None:
            for record in result.terminalRatings["terminalRating"]:
                terminal ={}
                for key in record:
                    terminal[key] = str(record[key])
            
            alldevices.append(terminal)

    except zeep.exceptions.Fault as fault:
        print("Error", fault.message, ":", SoapError(fault.message))

# print to stdout
json.dump(alldevices,sys.stdout, indent=4)
