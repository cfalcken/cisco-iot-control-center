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
import re
from requests.exceptions import RequestException

try:
    import zeep
except ImportError:
    pass
    
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

def get_data (url, username, password, params={}, method="get", jsondata={}, debug=False ):
    
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

            if method == "get":
                if username !='':
                    myResponse = requests.get(
                        url,
                        auth=(username,password),
                        params=params
                )
                else:
                    myResponse = requests.get(
                        url,
                        params=params
                    )
            elif method == "post":
                if username !='':
                    myResponse = requests.post(
                        url,
                        auth=(username,password),
                        json=jsondata,
                        params=params
                )
                else:
                    myResponse = requests.post(
                        url,
                        json=jsondata,
                        params=params
                    )
            elif method == "put":
                if username !='':
                    myResponse = requests.put(
                        url,
                        auth=(username,password),
                        json=jsondata,
                        params=params
                )
                else:
                    myResponse = requests.put(
                        url,
                        json=jsondata,
                        params=params
                    )
            else:
                sys.exit(f"Unknown method '{method}'")
     

            if myResponse.ok:
                print (f"Request successful", file=sys.stderr)
                return myResponse.content
            elif myResponse.status_code in [429,503,504]:
                delay+=delayinc
                print (f"Received HTTP error {myResponse.status_code}; retrying in {delay} seconds", file=sys.stderr)
                time.sleep(delay)
                continue
            elif myResponse.status_code == 400:
                print("Received HTTP error 400: Bad request", file=sys.stderr)
                return myResponse.content
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


def get_filename_from_header(response):
    # Attempt to extract filename from the Content-Disposition header
    content_disposition = response.headers.get('Content-Disposition')
    
    if content_disposition:
        filename_match = re.findall('filename=(.+)', content_disposition)
        if filename_match:
            return filename_match[0]
    # If Content-Disposition header is not present, use URL to derive filename
    return os.path.basename(response.url)

def print_download_stats(total_size, downloaded_size, start_time):
    elapsed_time = time.time() - start_time
    if elapsed_time > 0:
        speed = downloaded_size / elapsed_time  # in bytes per second
        if total_size > 0:
            percent_complete = (downloaded_size / total_size) * 100
            remaining_time = (total_size - downloaded_size) / speed if speed > 0 else 0

            print(f"\rDownloaded: {downloaded_size} / {total_size} bytes ({percent_complete:.2f}%) "
                  f"at {speed / 1024:.2f} KB/s, estimated time remaining: {remaining_time:.2f} seconds", end='', file=sys.stderr)
        else:
            print(f"\rDownloaded: {downloaded_size} bytes at {speed / 1024:.2f} KB/s", end='', file=sys.stderr)

def download_file(url, path, username, password, debug=False):

    try:

        if debug:
            http_client.HTTPConnection.debuglevel = 1
            logging.basicConfig()
            logging.getLogger().setLevel(logging.DEBUG)
            requests_log = logging.getLogger("requests.packages.urllib3")
            requests_log.setLevel(logging.DEBUG)
            requests_log.propagate = True

        # Initial request to get the filename
        #
        response = requests.get(url, auth=(username,password), stream=True)
        response.raise_for_status()
        filename = path + get_filename_from_header(response)

        print(f"Downloading to file name: {filename}", file=sys.stderr)

        #if os.path.exists(filename):
        #    # Get the file size
        #    file_size = os.path.getsize(filename)
        #else:
        #    file_size = 0
        file_size = 0

        content_size = int(response.headers.get('Content-Length', 0))
        if content_size > 0:
            total_size = content_size + file_size
        else:
            total_size = 0

        headers = {'Range': f'bytes={file_size}-'}
        with requests.get(url, auth=(username,password), headers=headers, stream=True) as response:

            # Raise an error if the request was unsuccessful
            response.raise_for_status()

            # Open the local file in write-binary mode
            with open(filename, 'wb') as file:

                downloaded_size = 0
                start_time = time.time()

                # Iterate over the response in chunks
                chunks=0
                for chunk in response.iter_content(chunk_size=8192):
                    # Filter out keep-alive new chunks
                    if chunk:
                        file.write(chunk)
                        file.flush()
                        downloaded_size += len(chunk)
                        chunks +=1
                    if chunks > 128:
                        print_download_stats(total_size, downloaded_size, start_time)
                        chunks = 0

    except RequestException as e:
        print(f"Download interrupted: {e}", file=sys.stderr)
        print("Attempting to resume the download in 30 seconds...", file=sys.stderr)

        time.sleep( 30 )

        # Recursive call to resume the download
        download_file(url, path, username, password, debug)

    print(f"Done.", file=sys.stderr)



