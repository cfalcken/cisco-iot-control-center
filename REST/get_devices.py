#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
----------------------------------------------------------------------
 Get list of devices via REST API
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

import requests 
import json 
import yaml
import os
from pathlib import Path
import argparse
import sys
import time

__author__ = "Christian Falckenberg"
__email__ = "cfalcken@cisco.com"
__version__ = "1.0.0"
__copyright__ = "Copyright (c) 2023 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"

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

delay=0
delayinc=1

devices=[]
page = 1
lastpage = False

while not lastpage:

    print(f"Requesting page {page} with delay {delay}", file=sys.stderr)
    myResponse = requests.get(
        settings[args.site]["resturl"] + "/devices",
        auth=((settings[args.site]["username"]),settings[args.site]["apikey"]),
        params={
            "accountId": args.account,
            "pageNumber": page,
            "modifiedSince": args.modified
            })
                             
    # For successful API call, response code will be 200 (OK)
    if(myResponse.ok):
    
        # Loading the response data into a dict variable
        # json.loads takes in only binary or string variables so using content to fetch binary content
        # Loads (Load String) takes a Json file and converts into python data structure (dict or list, depending on JSON)
        jData = json.loads(myResponse.content)
        page+=1
        lastpage = jData["lastPage"]
        devices = devices + jData["devices"]
    else:
        # If response code is not ok (200), print the resulting http error code with description
        print("Failure")
        myResponse.raise_for_status()
    
        # If API call returns the "limit exceeded" error, increase loop delay
        #
        if myResponse.status_code != requests.codes.ok:
            delay += delayinc
        else:
            if delay > delayinc:
                delay -= delayinc
            else:
                delay=0
 
    time.sleep( delay )

# Now we have all accounts in the list, and do whatever we want now. Here, just dump the JSON content
#
json.dump(jData["devices"],sys.stdout,indent=4)
