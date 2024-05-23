
"""
Filename: generation.py
Author: Tristan Kuhn
Date: 2023-05-23
License: TOW TRUCK SERVER LICENSE AGREEMENT
Description: Value generation for Tow Truck Servers

Usage:
    Provide a brief example of how to run the script.
    e.g., python your_script_name.py [options]

Dependencies:
    random
    string

Functions:
    - generate_random_seed: Generate seed for minecraft servers.

Classes:
    - None

Notes:
    Is redundant, but is left for future use.
    
"""
import random
import string
def generate_random_seed():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))