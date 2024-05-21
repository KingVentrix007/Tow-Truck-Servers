import os
import tkinter as tk
import customtkinter as ctk
from threading import Thread
from mods.modloader import download_server_jar
from mods.fabric import install_fabric_server
from mods.forge import install_forge_server
from file_utils.path_mangment import adjust_path
import json
import re
import subprocess
import psutil
from tkinter import messagebox,ttk

def add_entry(name: str, game_version: str,description,modloader, config_path='config.json',img=None):
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
        "gameVersion": game_version,
        "description": description,
        "modloader": modloader,
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

def get_server(display_name: str, config_path='config.json'):
    # Load existing config
    try:
        with open(config_path, 'r') as file:
            config = json.load(file)
    except FileNotFoundError:
        print("Config file not found.")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None

    # Search for the server with the specified display name
    for server in config.get('servers', []):
        if server.get('displayName') == display_name:
            return server
    
    print(f"Server with display name '{display_name}' not found.")
    return None
def install_server(name,version,modloader):
    if(modloader == "fabric"):
        install_fabric_server(name=name,version=version)
    elif(modloader == "forge"):
        install_forge_server(name=name,jar_file=version)
        
    else:
        return -1

def make_server(name, description, version,img,modloader):
    valid_server_name = name.replace(" ","")
    if(os.path.exists(valid_server_name)):
        return -1
    os.makedirs(f"./servers/{valid_server_name}", exist_ok=True)
    jar_download_window = ctk.CTk()
    jar_download_window.title("Downloading Server Jar")
    jar_download_window.geometry("30x40")
    progress_var = tk.DoubleVar(jar_download_window, 0.0)
    progressbar = ttk.Progressbar(jar_download_window, variable=progress_var, maximum=100)
    progressbar.pack(pady=10)
    def on_complete(name, version):
        jar_download_window.destroy()
        install_server(name, version, modloader)
        adjust_path() #TODO: Redo Path handling, way to much os.chdir() and back and forth, look into better solutions
        add_entry(name=name, game_version=version,description=description,modloader=modloader,img=img)
    

    
    download_thread = Thread(target=download_server_jar, args=(name, version, progress_var, on_complete,modloader))
    download_thread.start()
    
    jar_download_window.mainloop()

