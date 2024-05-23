
"""
Filename: path_management.py
Author: Tristan Kuhn
Date: 2023-05-23
License: TOW TRUCK SERVER LICENSE AGREEMENT
Description: Path management functions for Tow Truck Servers

Usage:
    Import path_management.py into whatever code you need

Dependencies:
    None

Functions:
    - adjust_path: Adjusts the path to be One before the servers folder


Classes:
    - None

Notes:
    None
    
"""
import os
def adjust_path():
    current_path = os.getcwd()
    print(f"Current path: {current_path}")

    if 'servers' in current_path:
        path_parts = current_path.split(os.sep)
        new_path_parts = []
        for part in path_parts:
            if part == 'servers':
                break
            new_path_parts.append(part)
        new_path = os.sep.join(new_path_parts)
        
        if new_path:
            os.chdir(new_path)
            print(f"Adjusted path: {new_path}")
        else:
            print("New path is empty. Path adjustment failed.")
    else:
        print("The current path does not contain 'servers'.")
