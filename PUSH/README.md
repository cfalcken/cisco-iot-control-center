# PUSH API receiver for Cisco IOT Control Center

Simple Python based receiver to implement a PUSH API receiver for events triggered by Control Center automation rules. Running the script will start the receiver listening on the specified port, and will just print the content of received events. Note that it tries to match the signature with the hashed timestamp together with the shared secret; this secret needs to match the one defined for the account that has created the automation rule.

