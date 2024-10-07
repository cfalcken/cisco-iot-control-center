#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
----------------------------------------------------------------------
CDRs per Account

Process the Data Usage Report of the Cisco IoT Control Center and 
identify the top accounts based on the number of CDR buckets required
(1 bucket = 300 CDR per device per month, estimated here as 10 CDR per
device per day for the daily usage report)
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
import time
import math

__author__ = "Christian Falckenberg"
__email__ = "cfalcken@cisco.com"
__version__ = "1.0.0"
__copyright__ = "Copyright (c) 2023 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"

# Define the header fields
#
ICCID = 1
ACCOUNTID = 4
DATAUSAGE = 13
DURATION = 21
CHARGINGID = 23
CLOSECAUSE = 24

# For later use
#
BILLABLE = 5
SIMSTATE = 7
SERVICETYPE = 8
RATEPLAN = 9
ZONE = 10
RAT = 36

# define and parse arguments
#
parser = argparse.ArgumentParser(
    description='Analyze CDRs per account from Data Usage Report of Cisco IoT Control Center".')
args = parser.parse_args()

# Read the CSV file from STDIN using the given delimiter
#
starttime = time.time()
print("Started reading CSV from STDIN at " +
      time.ctime(starttime), file=sys.stderr)
reader = csv.reader(sys.stdin, delimiter="|")

accounts = {}

# Read each line of the file extract information
#
print("Started processing at " + time.ctime(time.time()), file=sys.stderr)
for rid, row in enumerate(reader):

    if row[ACCOUNTID] == "Account ID":
        continue

    if rid % 100000 == 0:
        print("Processing row " + str(rid), file=sys.stderr)

    if row[ACCOUNTID] not in accounts:
        accounts[row[ACCOUNTID]] = {}

    iccids = accounts[row[ACCOUNTID]]
    if row[ICCID] not in iccids:
        iccids[row[ICCID]] = {}

    sessions = iccids[row[ICCID]]
    if row[CHARGINGID] not in sessions:
        sessions[row[CHARGINGID]] = [0 for i in range(8)]

    records = sessions[row[CHARGINGID]]

    # Store results:
    #   0: total number of records
    #   1: total duration
    #   2: total usage
    #   3: number of zero byte records
    #   4: number of time partials
    #   5: number of volume partials
    #   6: sum of duration for time partials
    #   7: sum of volume for volume partials
    #
    records[0] += 1
    records[1] += int(row[DURATION])
    records[2] += int(row[DATAUSAGE])
    if row[DATAUSAGE] == "0":
        records[3] += 1
    if (row[CLOSECAUSE] == "17") or (row[CLOSECAUSE] == "2"):
        records[4] += 1
        records[6] += int(row[DURATION])
    if (row[CLOSECAUSE] == "16") or (row[CLOSECAUSE] == "1"):
        records[5] += 1
        records[7] += int(row[DATAUSAGE])

endtime = time.time()
print("Finished processing " + str(rid+1) + " lines in " +
      str(int(endtime - starttime)) + " seconds", file=sys.stderr)

# Print the analysis
#
print("Preparing result", file=sys.stderr)
account_report = []
for account in accounts:
    total_iccids = 0
    total_sessions = 0
    total_records = 0
    total_usage = 0
    total_duration = 0
    total_zero_byte_records = 0
    total_time_partials = 0
    total_volume_partials = 0
    total_time_partial_duration = 0
    total_volume_partial_usage = 0
    average_time_partial_seconds = 0
    average_volume_partial_bytes = 0

    iccids = accounts[account]
    for iccid in iccids:
        total_iccids += 1

        sessions = iccids[iccid]
        for session in sessions:
            total_sessions += 1
            records = sessions[session]
            total_records += records[0]
            total_duration += records[1]
            total_usage += records[2]
            total_zero_byte_records += records[3]
            total_time_partials += records[4]
            total_volume_partials += records[5]
            total_time_partial_duration += records[6]
            total_volume_partial_usage += records[7]

    if total_time_partials > 0:
        average_time_partial_seconds = int(
            total_time_partial_duration / total_time_partials)

    if total_volume_partials > 0:
        average_volume_partial_bytes = int(
            total_volume_partial_usage / total_volume_partials)

    # Calculate the estimated CDR charge units for the account, which then would just need
    # to be multiplied with the CDR price per device
    # - dividing by 10 instead of 300 considers that the records are counted only for a day,
    #   but the result is then the estimated value for the month
    # - using int rounds the number down, so that this counts the extra blocks (if records per
    #   ICCID are below 10 then the result is 0)
    #
    cdrcharge = math.ceil((total_records * 30 - total_iccids * 300 ) / 300)

    account_report.append((
        account,
        total_iccids,
        total_sessions,
        total_records,
        int(total_records / total_iccids),
        cdrcharge,
        total_duration,
        int(total_duration/total_sessions),
        total_usage,
        total_zero_byte_records,
        total_time_partials,
        total_volume_partials,
        average_time_partial_seconds,
        average_volume_partial_bytes
    ))

# Report only accounts with extra CDR blocks
#
accounts_out = []
for account in account_report:
    if account[5] > 0:
        accounts_out.append(account)

# Sort the output based on the CDR blocks
#
accounts_out.sort(key=lambda tup: int(tup[5]), reverse=True)

# Print the account list
#
print("Account ID, Number of ICCIDs, Number of Sessions, Number of Records, Records per Device, CDR charge units, Total Duration, Average Session Duration, Total Usage, Zero Byte Records, Time Partials, Volume Partials, Average Time Partial Seconds, Average Volume Partial Bytes")

for account in accounts_out:
    print(*account, sep=",")

endtime = time.time()
print("Done after " + str(int(endtime - starttime)) + " seconds.", file=sys.stderr)
