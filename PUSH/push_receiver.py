#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
----------------------------------------------------------------------
Simple PUSH API receiver for Cisco IOT Control Center
to display the received data including signature verification
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

import xml.etree.ElementTree as ET
import http.server
import urllib.parse
import hmac
import hashlib
import base64
from xml.dom import minidom
import subprocess
import os
from pathlib import Path
import argparse
import yaml

__author__ = "Christian Falckenberg"
__email__ = "cfalcken@cisco.com"
__version__ = "1.0.0"
__copyright__ = "Copyright (c) 2023 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"

# Parse the command line to get the site name
# Optionally, define the port to run the server
#
parser = argparse.ArgumentParser(os.path.basename(__file__))
parser.add_argument("site", help="Name of the site as specified in settings.yaml", type=str)
parser.add_argument('-p', '--port', type=int, default='8888', help='Port to listen on for incoming requests')
args = parser.parse_args()

# Get the secret from external settings file
#
full_file_path = Path(__file__).parent.joinpath('../settings.yaml')
with open(full_file_path) as settings:
    settings = yaml.load(settings, Loader=yaml.Loader)

# Define a Push API handler
#
class PushAPIHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):

        def handle_session_stop(iccid):
            print(f"Session ended for ICCID {iccid}")

            # Below is an example for calling another script that handles this event
            # Modify as needed
            #subprocess.Popen(f"/home/ubuntu/CC/SOAP/get_usage_details.py {args.site} {iccid} 2023-01-01", shell=True)

        content_type = self.headers.get('Content-Type')
        if content_type.startswith('application/x-www-form-urlencoded'):
            print("Received push notification:")
 
            # Process the response
            #
            content_length  = int(self.headers.get('Content-Length'))
            post_data       = self.rfile.read(content_length)
            form_data       = urllib.parse.parse_qs(post_data.decode('utf-8'))
            event           = form_data["eventType"][0]
            signature       = form_data["signature2"][0]
            data            = form_data["data"][0]
            timestamp       = form_data["timestamp"][0]

            # create an HMAC-SHA256 hash of the timestamp using the secret key
            # and convert the resulting hash value to a string in hexadecimal format
            #
            hash     = hmac.new(bytes(settings[args.site]["secret"], 'utf-8'), bytes(timestamp, 'utf-8'), hashlib.sha256)
            hash_str = base64.b64encode(hash.digest()).decode('utf-8')

            # Print the content
            #
            print("Event            : " + event)
            print("Signature        : " + signature)
            print("Hashed timestamp : " + hash_str)
            if hash_str == signature:
                print("Signature verification successful")
            else:
                print("Signature verification failed")
                
            xml_data = ET.fromstring(data)
            xmlstr = minidom.parseString(ET.tostring(xml_data, encoding='utf8').decode('utf8')).toprettyxml(indent="   ")
            print("XML data         :")
            print(xmlstr)
            
            # Send a response back to the sender
            #
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Received push notification')

            # Handle the event
            #
            if event == "SESSION_STOP":
                iccid = xml_data.find("{http://api.jasperwireless.com/ws/schema}iccid").text
                handle_session_stop(iccid)

        else:
            # Notify the sender about the unexpected content type
            # 
            self.send_response(400)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Invalid content type')

# Start the server listening on the given port
#
with http.server.HTTPServer(("", args.port), PushAPIHandler) as httpd:
    print("Push API receiver listening on port", args.port)
#    httpd.socket = ssl.wrap_socket(httpd.socket,
#                               server_side=True,
#                               certfile='/tmp/le.pem',
#                               ssl_version=ssl.PROTOCOL_TLS)
    httpd.serve_forever()
