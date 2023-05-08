# cisco-iot-control-center

*Cisco IOT Control Center Sample Scripts*

---

## Motivation

This collection of scripts demonstrate the usage of the REST, SOAP and PUSH API interfaces of the Cisco IOT Control Center solution and how these APIs can be used to retrieve information from the system besides the GUI and the report files. Additional scripts are provided that help processing the "JPO reports" that are created by Control Center.

Note that for accessing the APIs an API key (REST) and a license key (SOAP) is needed; for the PUSH API it is also necessary to configure a shared secret to validate the signature of incoming requests. These user and site specific settings are loaded by each script from a file called "settings.yaml".

## Installation

Simply make sure that your system supports the Python interpreter and pip, and install any additional packages required Python packages with this command:

````
pip install -r requirements.txt
````

Rename the file settings-sample.yaml to settings.yaml, and modify the information in this file with the individual user name and keys that allow you to access the API of a specific Control Center site. You can find these keys and the URLs to use in the Knowledge Base within Control Center.

## Usage

If you run any of the scripts without arguments then you get a message which arguments are mandatory; you can also see a detailed help including optional parameters with "-h". Most scripts require at least the site name, which needs to match the name specified in the settings.yaml file.

## Authors & Maintainers

Responsible for the creation and maintenance of this project:

- Christian Falckenberg <cfalcken@cisco.com>

## Credits

Please refer to the Knowledge Base in the Cisco IoT Control Center solution for a detailed documentation of all REST, SOAP and PUSH API functions including additional code smaples in other languages

## License

This project is licensed to you under the terms of the [Cisco Sample
Code License](./LICENSE).
