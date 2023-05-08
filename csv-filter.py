#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
----------------------------------------------------------------------
Filter a CSV from STDIN to print only selected columns and when
contents of a column match given filter expression
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
import os
import re
import csv
import argparse
import errno
from contextlib import suppress

__author__ = "Christian Falckenberg"
__email__ = "cfalcken@cisco.com"
__version__ = "1.0.0"
__copyright__ = "Copyright (c) 2023 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"

# define and parse arguments
#
parser = argparse.ArgumentParser(description='Filter for CSV files to print only selected columns and when they match a pattern".')

parser.add_argument('-c', '--columns', type=str, nargs='+', help='columns to select in output')
parser.add_argument('-f', '--filters', type=str, nargs='+', help='columns with values to match')
parser.add_argument('-d', '--delimiter', type=str, default=',', help='delimiter between fields in input')
parser.add_argument('-n', '--noheader', action='store_false', help='do not print a header')

# parse the arguments from the command line
#
args = parser.parse_args()

# read in the input from standard input and extract the header row
#
#reader = csv.reader(sys.stdin,delimiter=args.delimiter, quoting=csv.QUOTE_NONE)
reader = csv.reader(sys.stdin,delimiter=args.delimiter)
header = next(reader)

# If no argument was given, print the list of possible columns and exit
#
if args.columns == None:
    print("Provide the columns to be printed by using the -c option and specifying the index from the list below:")
    for i in range(0,len(header)):
        print (i+1,":",header[i])
    print("""
Instead of specifying each column (e.g. '1 4 12'), you can also provide a range (e.g. '1-3 5 10-12')    
With the -f option, you can specify the field number with `=` and a filter string, which is processed as a regular expression. For example:
.*abc: any characters followed by 'abc'
^abc$: only matches 'abc' exactly
^$: matches an empty value
.+: matches if non-empty (one ore ore of any character)
Refer to https://docs.python.org/3/howto/regex.html for the full set of special patterns

Example:
cat file.csv | ./csv-filter.py -c 1-4 -f 12=".*Hello"
Prints only columns 1-4 and only when column 12 contains the string "Hello"

    """)
    exit()

# Parse the list of column arguments and build the complete list
#
columnlist=[]
for column in args.columns:

    # check if a range of columns is given
    #
    c = column.split("-")
    if c[0] != column:
        for f in range(int(c[0]), int(c[1])+1):
            if f not in columnlist:
                columnlist.append(f)
    else:
        if c[0].isdigit():
            columnlist.append(int(c[0]))
        else:
            columnlist.append(header.index(c[0])+1)

# Parse the list of filters
# 
filterlist={}
if args.filters != None:
    for filter in args.filters:
        f = filter.split("=")
        if f[0] != filter:
            filterlist[f[0]] = f[1]

# write the selected columns to standard output
#
writer = csv.writer(sys.stdout)
if args.noheader == True:
    writer.writerow([header[i-1] for i in columnlist])

# cycle through the rest of the input and print only selected colums and only when a filter matches, if provided
#
try:
    data = []
    for row in reader:
        selected_row=[]
        filtered = False
        for f in filterlist:
            if not re.match(filterlist[f], row[int(f)-1]):
                filtered = True

        if not filtered:
            for c in columnlist:
                selected_row.append(row[c-1])
            writer.writerow(selected_row)

except IOError as e:
    if e.errno == errno.EPIPE:
        pass
