#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
----------------------------------------------------------------------
sgt - statistics generator for tables

Simply counts all values in the specified columns for a CSV file 
provided via STDIN
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
import csv
import argparse

__author__ = "Christian Falckenberg"
__email__ = "cfalcken@cisco.com"
__version__ = "1.0.0"
__copyright__ = "Copyright (c) 2023 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"

# define and parse arguments
#
parser = argparse.ArgumentParser(description='Filter for CSV files to count values per column".')
parser.add_argument('-d', '--delimiter', type=str, default=',', help='delimiter between fields in input')
parser.add_argument('-c', '--columns', type=str, nargs='+', help='columns to select in output')
args = parser.parse_args()

# Read the CSV file from STDIN using the given delimiter and parse the 
# first line into the header
#
reader = csv.reader(sys.stdin,delimiter=args.delimiter)
header = next(reader)

if args.columns != None:
    
    # Initialize the dictionary
    #
    colstats = {}
    for c in args.columns:
        colstats[c] = {}
    
    # Read each line of the file and count the values
    #
    for row in reader:
        for c in args.columns:
            colstats[c][row[int(c)-1]] = colstats[c].get(row[int(c)-1],0) + 1
   
    # Print the calculated statistics for each column
    #   
    for c in args.columns:
        for key in sorted(colstats[c].keys()):
#            print(f"{c:2s} : {key:50s} - {colstats[c][key]:10d}")
            print(c + "," + key + "," + str(colstats[c][key]))

# If no column option was provided, print a help with the list of columns that can be selected
#
else:
    print("Provide the columns to be analyzed by using the -c option and specifying one or more indices from the list below:")
    for i in range(0,len(header)):
        print (i+1,":",header[i])
