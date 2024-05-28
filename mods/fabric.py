
"""
Filename: fabric.py
Author: Tristan Kuhn
Date: 2024-05-24
License: TOW TRUCK SERVER LICENSE AGREEMENT
Description: Fabric module for Tow Truck Server

Usage:
    Import fabric into necessary code 

Dependencies:
    tkinter
    requests


Functions:
    - load_cache: Loads the fabric cache
    - save_cache: Saves the fabric cache
    - run_command: Runs the command
    - GetLatestStableFabricServerURL: Gets the latest stable fabric server jar file url
    - install_fabric_server: Installs the fabric server

Classes:
    - ClassName: Brief description of what the class does.

Notes:
    Any additional notes or information.
    
"""

from minecraft.minecraft_versions import minecraft_versions
import requests
import json
import os
import tkinter as tk
import threading as Thread
import subprocess
from tkinter import messagebox
from file_utils.path_management import adjust_path
from config.errors import err_code_process_closed
from file_utils.path_management import adjust_path

cache_file = "fabric_jar_cache.json"

def load_cache():
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(cache_file, 'w') as f:
        json.dump(cache, f, indent=4)

def run_command(command, output_widget):
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        for line in iter(process.stdout.readline, ""):
            output_widget.insert(tk.END, line)
            output_widget.see(tk.END)
            if "The server installed successfully" in line:
                output_widget.insert(tk.END, "\nInstallation complete.Close the window to continue\n")
                output_widget.see(tk.END)
                messagebox.showinfo("Installation complete","The installation is complete. You must close the window to continue")
                # if root and root.winfo_exists():  # Check if root window exists
                    # print("ROOT")
                
        process.stdout.close()
        process.wait()

def GetLatestStableFabricServerURL(version):
    cache = load_cache()

    # Check if the version is already cached
    if version in cache:
        cached_data = cache[version]
        if cached_data.get('url') and cached_data.get('fabric_version'):
            print(f'Using cached URL for version {version}')
            return cached_data['url']

    # If not in cache or cache is invalid, fetch from the Fabric API
    loader_info_url = f'https://meta.fabricmc.net/v2/versions/loader/{version}'
    response = requests.get(loader_info_url)
    if response.status_code == 200:
        data_list = response.json()
        stable_versions = [data.get('loader', {}).get('version', '') for data in data_list if data.get('loader', {}).get('stable', False)]
        latest_stable_version = max(stable_versions, default=None)
        if latest_stable_version:
            download_url = f'https://meta.fabricmc.net/v2/versions/loader/{version}/{latest_stable_version}/1.0.1/server/jar'
            # Update the cache with the new data
            cache[version] = {
                'fabric_version': latest_stable_version,
                'url': download_url
            }
            save_cache(cache)
            return download_url
        else:
            print('No stable versions found in the response.')
            return -2
    else:
        print('Failed to fetch the loader version information.')
        return -3

def install_fabric_server(version,name):
    # java -Xmx2G -jar fabric-server-mc.1.20.6-loader.0.15.11-launcher.1.0.1.jar nogui
    root = tk.Tk()
    root.title("Installing Server")

    output_widget = tk.Text(root, wrap="word")
    output_widget.pack(expand=True, fill="both")
    use_name = name.replace(" ","")
    os.chdir(f"./servers/{use_name}")
    jar_file = f"fabric_installer_{version}.jar"
    command = ["java","-Xmx2G","-jar",jar_file,"nogui"]
    thread = Thread.Thread(target=run_command, args=(command, output_widget))
    thread.start()
    root.mainloop()


def run_fabric_server(server_info,text_widget,on_finish):
    adjust_path()
    b_path = os.getcwd()
    path = server_info.get('path', "/fake/")
    java = server_info.get('javaPath', "java.eze")
    java = os.path.join(b_path,java)
    os.chdir(path)
    java = os.path.normpath(java)
    if(os.name != "nt"):
        java = java.replace("\\","/")
    java = java+".exe"
    if 'WSL_DISTRO_NAME' in os.environ:
        # Convert Windows path to WSL path
        java = java.replace('\\', '/')
        # java = f'/mnt/{java[0].lower()}/{java[2:]}'
        java = os.path.normpath(java)

    print("Using java: %s" % java)
    print(os.getcwd())
    if(os.path.exists(java) != True):
        print("Java does not exist: %s" % java)
        exit(1)
    ram = server_info.get('ram', "2G")
    jar_version = server_info.get("gameVersion","0.0.0")
    jar_file = f"fabric_installer_{jar_version}.jar"
    cmd = f"{java} -Xmx{ram} -jar {jar_file} nogui %*"
    global process  # Declare process as a global variable
    process = None
    def run_command(command):
        global process
        print(command)
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        try:
            for line in iter(process.stdout.readline, ""):
                # print(line)
                formatted_output,color = format_output_as_html(line)
                try:
                    text_widget.insert(tk.END, formatted_output,color)
                    text_widget.see(tk.END)  # Auto-scroll to the end
                except Exception as e:
                    print(e)
            process.stdout.close()
            process.wait()
            process.pid
            on_finish(server_info,text_widget)
        except ValueError:
            name = server_info.get("displayName",'None')
            print(f"{err_code_process_closed}:Server{name} tried to read from stdout when stdout was closed")
            # on_finish(server_info)

    def format_output_as_html(output):
        return f'{output}','error'

    thread = Thread.Thread(target=run_command, args=(cmd,), daemon=True)
    thread.start()
    while(process == None):
        # Wait for the process to become valid
        pass
    adjust_path()
    return process
