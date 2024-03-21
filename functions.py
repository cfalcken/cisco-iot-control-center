#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
----------------------------------------------------------------------
Functions used in all scripts

Disclaimer: 
This script uses the internal API which is used by the GUI and not the
official REST or SOAP APIs. This interface is  not documented and not
supported, and any improper usage may impact the system.
Use at your own risk!
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

import os
import sys
import yaml
import traceback
import getpass
import requests
import time
import logging
import http.client as http_client
import json
import zeep

def load_site_settings(site):

    try:
        settingsfile = os.getenv("CCSETTINGS", default=os.getenv("HOME") + "/settings.yaml")
        with open(settingsfile) as settings:
            settings = yaml.load(settings, Loader=yaml.Loader)
    except Exception as error:
        print(f"Could not process settings file {settingsfile}: Error {error}", file=sys.stderr)
        print(traceback.format_exc())
        exit(1)

    if site not in settings:
        sys.exit(f"ERROR: Site {site} is not defined in settings file {settingsfile}")
    
    if "password" not in settings[site]:
        settings[site]["password"]=getpass.getpass("Please enter password for user " + settings[site]["username"] + " on site " + site + ": ")

    return settings[site]

def get_data (url, username, password, params={}, debug=False):
    
    if debug:
        http_client.HTTPConnection.debuglevel = 1
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True

    # Retry requests up to 5 times if needed
    #
    delay = 0
    delayinc = 10

    for _ in range(5):
        try:
            myResponse = requests.get(
                url,
                auth=(username,password),
                params=params
            )
            if myResponse.ok:
                return myResponse.content
            elif myResponse.status_code in [429,503,504]:
                delay+=delayinc
                print (f"Received HTTP error {myResponse.status_code}; retrying in {delay} seconds", file=sys.stderr)
                time.sleep(delay)
                continue
            elif myResponse.status_code == 401:
                sys.exit (f"Received HTTP error 401: Check username and password")
            elif myResponse.status_code == 404:
                sys.exit (f"Received HTTP error 404: Check URL '{url}'")
            elif myResponse.status_code == 500:
                print(f"Received HTTP error 500:", file=sys.stderr)
                print (myResponse.text, file=sys.stderr)
                for key,value in params.items():
                    if key == "search":
                        print ("  search:", file=sys.stderr)
                        print (value, file=sys.stderr)
                        properties = json.loads(value)
                        for property in properties:
                            print (f"    property: {property}", file=sys.stderr)
                            print (f"      filter: {property['property']} {property['type']} {property['value']}", file=sys.stderr)
                    else:
                        print (f"  {key}: {value}")
                sys.exit(f"Check parameters for URL '{url}'")
            else:
                sys.exit (f"Received unexpected HTTP error {myResponse.status_code}")

        except requests.exceptions.HTTPError as errh:
            sys.exit (f"Http Error: {errh}")
        except requests.exceptions.ConnectionError as errc:
            delay+=delayinc
            print (f"Error Connecting: {errc}, retrying in {delay} seconds", file=sys.stderr)
            time.sleep(delay)
        except requests.exceptions.Timeout as errt:
            sys.exit (f"Timeout Error: {errt}")
        except requests.exceptions.RequestException as err:
            sys.exit (f"Oops, some unexpected error: {err}")

    sys.exit ("Giving up after 5 retries")

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

