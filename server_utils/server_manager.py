"""
Filename: your_script_name.py
Author: Tristan Kuhn
Date Created: 2024-05-24
License: TOW TRUCK SERVER LICENSE AGREEMENT
Description: This script provides functionalities for managing game servers, including adding and removing server entries, loading and saving server properties, and retrieving all servers from the configuration.

Usage:
    Import the code into the necessary code

Dependencies:
    - json
    - shutil
    - server_utils.create_server (custom module)
    - subprocess
    - os
    - psutil
    - tkinter
    - tkinter.messagebox

Functions:
    - remove_server_by_display_name: Removes a server from the configuration by its display name.
    - get_all_servers: Retrieves all servers from the configuration.
    - load_properties: Loads server properties from a file.
    - save_properties: Saves server properties to a file.
    - del_server: Deletes a server by its name.
    - add_entry: Adds a new server entry to the configuration.

Classes:
    None

Notes:
    Ensure that the custom module server_utils.create_server is available in the project.
"""
import json
import shutil
from server_utils.create_server import get_server
import subprocess
import os
import psutil
import tkinter as tk
from tkinter import messagebox
def remove_server_by_display_name(display_name: str, config_path='config.json'):
    try:
        with open(config_path, 'r') as file:
            config = json.load(file)
    except FileNotFoundError:
        print("Config file not found.")
        return False
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return False

    servers = config.get('servers', [])

    updated_servers = [server for server in servers if server.get('displayName') != display_name]
    
    config['servers'] = updated_servers

    try:
        with open(config_path, 'w') as file:
            json.dump(config, file, indent=4)
        print(f"Server with display name '{display_name}' removed successfully.")
        return True
    except Exception as e:
        print(f"Error writing to config file: {e}")
        return False
def get_all_servers(config_path='config.json'):
    try:
        with open(config_path, 'r') as file:
            config = json.load(file)
    except FileNotFoundError:
        print("Config file not found.")
        return []
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return []

    return config.get('servers', [])
def load_properties(file_path):
    properties = {}
    with open(file_path, 'r') as file:
        for line in file:
            if '=' in line:
                key, value = line.strip().split('=', 1)
                properties[key] = value
    return properties
def save_properties(file_path, properties):
    with open(file_path, 'w') as file:
        for key, value in properties.items():
            file.write(f"{key}={value}\n")

def del_server(name: str):
    data = get_server(name)
    path = data["path"]
    remove_server_by_display_name(name)
    shutil.rmtree(path)

def add_entry(name: str, game_version: str, modloader,description,img,config_path='config.json'):
    display_name = name

    # Retrieve Java version
    try:
        java_version_output = subprocess.check_output(['java', '-version'], stderr=subprocess.STDOUT)
        java_version_output = java_version_output.decode('utf-8')
        java_version = java_version_output.split('\n')[0].split('"')[1]
    except Exception as e:
        print(f"Error retrieving Java version: {e}")
        return

    # Retrieve Java path
    try:
        if os.name == 'nt':  # Windows
            java_path_output = subprocess.check_output(['where', 'java'])
        else:  # Unix-like (Linux, macOS)
            java_path_output = subprocess.check_output(['which', 'java'])
        java_path = java_path_output.decode('utf-8').strip()
    except Exception as e:
        print(f"Error retrieving Java path: {e}")
        return

    # Determine RAM allocation
    total_memory = psutil.virtual_memory().total / (1024 ** 3)  # Convert bytes to GB
    if total_memory > 8:
        allocated_ram = 4
    elif total_memory >= 4:
        allocated_ram = 3
    else:
        allocated_ram = 2
        # Show Tkinter warning
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        messagebox.showwarning("RAM Allocation Warning", "The system has less than 4GB of RAM. The server may experience performance issues.")
        root.destroy()

    # Create new entry
    use_name = name.replace(" ", "")
    new_entry = {
        "displayName": display_name,
        "path": f"./servers/{use_name}",
        "description": description,
        "modloader":modloader,
        "gameVersion": game_version,
        "javaVersion": java_version,
        "javaPath": java_path,
        "ram": f"{allocated_ram}G",
        "image": f"{img}"
    }

    # Load existing config
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config = json.load(file)
    except FileNotFoundError:
        config = {"servers": []}
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return

    # Add new entry to the config
    config['servers'].append(new_entry)

    # Save updated config
    try:
        with open(config_path, 'w') as file:
            json.dump(config, file, indent=4)
        print("New entry added successfully.")
    except Exception as e:
        print(f"Error writing to config file: {e}")