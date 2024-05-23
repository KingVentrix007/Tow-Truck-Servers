
"""
Filename: globals.py
Author: Tristan Kuhn
Date: 2023-05-23
License: TOW TRUCK SERVER LICENSE AGREEMENT
Description: A config file containing globals for all the code

Usage:
    Simple library for Tow Truck Server

Dependencies:
    No Dependencies
Functions:
    - is_server_running: Returns true if the server is running
    - set_server_running: Sets the server to running
    - set_server_stopped: Sets the server to stopped

Classes:
    - No classes

Notes:
    Try to keep using the comment style
    
"""
# Temporary variable to prevent multiple servers from running simultaneously
# Currently running multiple servers will lead to EBADF
# See Glitch22/05/2024/1 for more details
server_running = False
def is_server_running():
    return server_running
def set_server_running():
    global server_running
    server_running = True
def set_server_stopped():
    global server_running
    server_running = False

# Global variables for width and height of icons
tab_icon_width = 30
tab_icon_hight = 30

#Default name for servers, if .get("displayName") doesn't work this will be returned
default_server_name = "Unnamed Server"