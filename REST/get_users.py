#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
----------------------------------------------------------------------
 Get a list of all users via REST API
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
parser.add_argument('-f', '--fields', type=str, default=',', help='Fields to print from JSON')
parser.add_argument("-d", "--debug", help="Enable debug output", action='store_true' )
args = parser.parse_args()

# Load settings for the site
#
settings = functions.load_site_settings(args.site)

# Build the fields selector in case it was provided
#
fields =''
if args.fields != '':
    fields = '?fields=' + args.fields

users=[]
page = 1
lastpage = False

while not lastpage:

    print(f"Requesting page {page}", file=sys.stderr)

    params={"pageNumber": page}

    jData = json.loads(functions.get_data(
        settings["resturl"] + "/users" + fields,
        settings["username"], 
        settings["apikey"], 
        params, 
        args.debug))
    users += jData["users"]
    page+=1
    lastpage = jData["lastPage"]

# Dump the result
#
print(json.dumps(users, indent=4))
