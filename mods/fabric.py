from minecraft.minecraft_versions import minecraft_versions
import requests
import json
import os
import tkinter as tk
import threading as Thread
import subprocess
from tkinter import messagebox

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

def install_fabric_server(jar_file,name):
    # java -Xmx2G -jar fabric-server-mc.1.20.6-loader.0.15.11-launcher.1.0.1.jar nogui
    root = tk.Tk()
    root.title("Installing Server")

    output_widget = tk.Text(root, wrap="word")
    output_widget.pack(expand=True, fill="both")
    use_name = name.replace(" ","")
    os.chdir(f"./servers/{use_name}")
    command = ["java","-Xmx2G","-jar",jar_file,"nogui"]
    thread = Thread(target=run_command, args=(command, output_widget))
    thread.start()
    root.mainloop()