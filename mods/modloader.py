
"""
Filename: modloader.py
Author: Tristan Kuhn
Date: 2024-05-24
License: TOW TRUCK SERVER LICENSE AGREEMENT
Description: Module of mod loader specific code
Usage:
    Import the module into the necessary code

Dependencies:
    requests

Functions:
    - download_forge: Starts the forge installer jar download
    - download_fabric: Starts the fabric server jar download 
    - download_server_jar: Downloads the server jar using one of the above functions

Classes:
    - ClassName: Brief description of what the class does.

Notes:
    Any additional notes or information.
    
"""
from mods.fabric import GetLatestStableFabricServerURL
from mods.forge import GetRecommendedURL
from minecraft.minecraft_versions import minecraft_versions
import requests
from tkinter import messagebox
valid_mod_loaders = ["forge","fabric"]

def download_forge(version:str,name:str,progress_var,on_complete):
    exit_code = 0
    forge_installer_url = GetRecommendedURL(version)
    response = requests.get(forge_installer_url, stream=True)
    if(response.status_code != 200):
        messagebox.showerror("Download error",f"Failed to download forge jar for {version}")
        exit_code = -1
    log(response.headers)
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024 # 1 Kibibyte
    bytes_so_far = 0
    use_name = name.replace(" ","")
    with open(f"./servers/{use_name}/forge_installer_{version}.jar", "wb") as file:
        for data in response.iter_content(block_size):
            file.write(data)
            bytes_so_far += len(data)
            progress = int(bytes_so_far * 100 / total_size)
            progress_var.set(progress)
    on_complete(name, version,exit_code)
def download_fabric(version:str,name:str,on_complete):
    exit_code = 0
    fabric_install_url = GetLatestStableFabricServerURL(version)
    log(fabric_install_url)
    response = requests.get(fabric_install_url, stream=True)
    if(response.status_code != 200):
        messagebox.showerror("Download error","Failed to download fabric server jar file.")
        exit_code = -1
    else:
        log(response.headers)
        block_size = 1024 # 1 Kibibyte
        use_name = name.replace(" ","")
        with open(f"./servers/{use_name}/fabric_installer_{version}.jar", "wb") as file:
            for data in response.iter_content(block_size):
                file.write(data)
    on_complete(name, version,exit_code)
def download_server_jar(name:str, version:str,progress_var,on_complete,modloader:str):
    if(version not in minecraft_versions):
        return -1
    if(modloader not in valid_mod_loaders):
        return -2
    if(modloader == "fabric"):
        download_fabric(name=name, version=version,on_complete=on_complete)
        return 0
    elif(modloader == "forge"):
        download_forge(name=name, version=version,progress_var=progress_var,on_complete=on_complete)
        return 0
    