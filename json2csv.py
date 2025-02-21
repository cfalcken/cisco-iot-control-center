#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
----------------------------------------------------------------------
convert JSON data from STDIN to CSV on STDOUT
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

import sys
import json
import csv
import errno

__author__ = "Christian Falckenberg"
__email__ = "cfalcken@cisco.com"
__version__ = "1.0.0"
__copyright__ = "Copyright (c) 2023 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"


# Flatten a nested JSON object into a dictionary
# with keys as the original keys joined by '_' characters
# to represent nested levels.
#
def flatten_json(nested_json, parent_key=''):
    items = []
    for key, value in nested_json.items():
        new_key = parent_key + '_' + key if parent_key else key
        if isinstance(value, dict):
            items.extend(flatten_json(value, new_key).items())
        elif isinstance(value, list):
            for i,v in enumerate(value):
                list_key = new_key + str(i+1)
                if isinstance(value, dict):
                    items.extend(flatten_json(v, list_key).items())
                else:
                    items.append((new_key, value))
        else:
            items.append((new_key, value))
    return dict(items)

# Extract all possible keys from a flat JSON object
#
def extract_json_keys(json_data):
    keys = set()
    for item in json_data:
        keys |= set(item.keys())
    return keys

# Open JSON from STDIN
#
try:
    with open(sys.stdin.fileno()) as json_file:
        json_data = json.load(json_file)
except Exception as error:
    sys.exit(f"ERROR: Could not process JSON input: {error}")

if "data" in json_data:
    json_data = json_data["data"]

# Flatten the JSON object into a list of dictionaries
#
flat_data = []
for item in json_data:
    flat_item = flatten_json(item)
    flat_data.append(flat_item)

# Extract all possible keys from the JSON input
header = sorted(list(extract_json_keys(flat_data)))

# now we will open a file for writing
#
data_file = open(sys.stdout.fileno(), 'w')

# create the csv writer object
#
csv_writer = csv.DictWriter(data_file,fieldnames=header)

# add the header to the file
#
csv_writer.writeheader()

# write to STDOUT and catch the exception that the STDOUT may not be processed
# 
try:
    for item in flat_data:
        # sort the item's keys to match the header
        sorted_item = {key: str(item.get(key,"-")).replace('\n','').replace(',',' ') for key in header}
        csv_writer.writerow(sorted_item)

    data_file.close()

except IOError as e:
    if e.errno == errno.EPIPE:
      pass

