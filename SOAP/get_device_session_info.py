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

# Parse the command line to get the site name and ICCID
#
parser = argparse.ArgumentParser(os.path.basename(__file__))
parser.add_argument("site", help="Name of the site as specified in settings.yaml", type=str)
parser.add_argument("iccid", help="Device ICCID", type=str)
args = parser.parse_args()

# Get the settings (URL, username, apikey) from external file
#
full_file_path = Path(__file__).parent.joinpath('../settings.yaml')
with open(full_file_path) as settings:
    settings = yaml.load(settings, Loader=yaml.Loader)

print("Getting details for ICCID", args.iccid, file=sys.stderr)

url         = settings[args.site]["wsdlurl"] + '/Terminal.wsdl'
soap_action = 'http://api.jasperwireless.com/ws/service/terminal/GetSessionInfo'
messageId   = '123456'
version     = '1'

# Create a SOAP client
#
client = Client(url, wsse=UsernameToken(settings[args.site]["username"], settings[args.site]["password"]))

# Set SOAP action in the header
#
client.transport.session.headers['SOAPAction'] = soap_action

# Call the GetTerminalDetails method
#
try:
    result = client.service.GetSessionInfo(
        messageId=messageId, 
        version=version, 
        licenseKey=settings[args.site]["licensekey"],
        iccid=args.iccid)

    # Print the result
    print(result.sessionInfo)

except zeep.exceptions.Fault as fault:
    print("Error", fault.message, ":", SoapError(fault.message))
