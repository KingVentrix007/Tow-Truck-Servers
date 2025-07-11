"""
Filename: ModeMenu.py
Author: Tristan Kuhn
Date Created: 2024-05-24
License: TOW TRUCK SERVER LICENSE AGREEMENT
Description: This script provides a graphical user interface for managing mods in a game server. It allows users to enable or disable mods by toggling switches for each mod. The script scans the "mods" directory within the server directory and displays all ".jar" and ".disabled" files as available mods.

Usage:
    This script is typically imported and used in conjunction with a GUI application for managing game servers.

Dependencies:
    - customtkinter
    - os

Functions:
    - mod_menu: Creates a mod management window with GUI components for toggling mods.

Classes:
    None

Notes:
    - This script relies on the customtkinter module for GUI components.
    - Mods are expected to be stored in the "mods" directory within the server directory.
"""
import customtkinter as ctk
import os
import tkinter as tk
from config.ui_config import default_color
import json
import requests
import io
from PIL import Image, ImageTk
from tkinter import messagebox
import threading
from time import sleep
import tempfile
import shutil
from tkinter import ttk
import mods.apiv2 as apiv2
import urllib.request
from config.debug import log
# Define a flag to signal the thread to stop
stop_search_thread = threading.Event()

def download_file(url, local_filename, progress, root, label, callback=None):
    with requests.get(url, stream=True) as response:
        response.raise_for_status()
        total_length = int(response.headers.get('content-length', 0))
        downloaded = 0

        with open(local_filename, 'wb') as out_file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    out_file.write(chunk)
                    downloaded += len(chunk)
                    progress["value"] = (downloaded / total_length) * 100
                    root.update_idletasks()

    if callback:
        callback()
def ensure_config_exists(config_path):
    if not os.path.exists(config_path):
        with open(config_path, 'w') as config_file:
            json.dump({"mods": []}, config_file)

def load_config(config_path):
    with open(config_path, 'r') as config_file:
        return json.load(config_file)

def save_config(config_path, config):
    with open(config_path, 'w') as config_file:
        json.dump(config, config_file, indent=4)

def show_waiting_window(mod_title):
    waiting_root = tk.Toplevel()
    waiting_root.title("Please Wait")
    waiting_label = ttk.Label(waiting_root, text=f"Searching for mod URLs for {mod_title}...\nThis may take a while, please be patient")
    waiting_label.pack(pady=20, padx=20)
    return waiting_root

def close_waiting_window(waiting_root):
    if waiting_root:
        waiting_root.destroy()

def fetch_mod_urls(mod_data, server_info):
    mod_urls = apiv2.get_download_urls(mod_data["project_id"], server_info.get("gameVersion", "0.0"), server_info.get("modloader", "null"))
    log(mod_urls)
    if(len(mod_urls) >=1):
        return mod_urls[0]
    return None 

def download_mod(mod_data, server_info):
    server_folder = server_info.get("path")
    config_path = os.path.join(server_folder, 'towtruckconfig.json')
    mod_id = mod_data["project_id"]
    log("MOD_DATA=", mod_data)
    
    ensure_config_exists(config_path)
    config = load_config(config_path)   
    if mod_id not in [mod_id for mod in config["mods"] for mod_id in mod.keys()]:
        pass
    else:
        log(f"Mod {mod_id} is already installed, skipping download.")
        return

    waiting_window = show_waiting_window(mod_data.get("title"))

    def download_mod_files():
        nonlocal config

        urls = fetch_mod_urls(mod_data, server_info)
        if(urls == None):
            messagebox.showerror("Failed to get mod urls","Failed to get mod_urls, please report this error, with the mod name, server version and mod loader")
        else:
            url = urls["url"]
            mod_file_name = os.path.basename(url)
            config["mods"].append({mod_id: mod_file_name})
            save_config(config_path, config)

            dependencies = urls["dependencies"]
            close_waiting_window(waiting_window)
            mod_folder = os.path.normpath(os.path.join(server_info.get("path", ""), "mods"))
            os.makedirs(mod_folder, exist_ok=True)

            root = tk.Tk()
            root.title("Download Progress")
            mod_name = mod_data["title"]
            label = ttk.Label(root, text=f"Downloading mod {mod_name}...")
            label.pack(pady=10)
            progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
            progress.pack(pady=10)

            def start_download():
                local_filename = os.path.join(mod_folder, mod_file_name)
                download_file(url, local_filename, progress, root, label, callback=lambda: download_dependencies(dependencies, config, config_path, mod_folder, progress, root, label))
                config["mods"].append({mod_id: mod_file_name})
                log("config45 = ",config)
                save_config(config_path, config)
                log(f"Downloaded mod to {local_filename}")

            threading.Thread(target=start_download).start()
            root.mainloop()
            

    threading.Thread(target=download_mod_files).start()
def download_dependencies(dependencies, config, config_path, mod_folder, progress, root, label):
    label.config(text="Mod download complete! Downloading dependencies...")
    for dep in dependencies:
        dep_id = dep["id"]
        dep_url = dep["url"]
        #EEE
        log(f"dependencies {dep_id} url: {dep_url}" )
        if dep_id not in [mod_id for mod in config["mods"] for mod_id in mod.keys()] and dep_url:
            dep_file_name = os.path.basename(dep_url)
            local_dep_filename = os.path.join(mod_folder, dep_file_name)
            download_file(dep_url, local_dep_filename, progress, root, label)
            config["mods"].append({dep_id: dep_file_name})
            save_config(config_path, config)
        else:
            log(f"Dependency {dep_id} already exists, skipping download.")
    label.config(text="All downloads complete!")
    log("Downloaded all dependencies.")
    root.destroy()
def render_mod(canvas, mod_data, server_info):
    mod_frame = ctk.CTkFrame(canvas, bg_color=default_color)
    mod_frame.pack(side=ctk.TOP, anchor=ctk.W, fill=ctk.X)

    mod_info_frame = ctk.CTkFrame(mod_frame, bg_color=default_color)
    mod_info_frame.pack(side=ctk.LEFT)

    # Create and pack the mod label with the image
    mod_label = ctk.CTkLabel(mod_info_frame, text=mod_data['title'] + " by " + str(mod_data.get("author", "None")), fg_color=default_color, bg_color=default_color)

    mod_label.pack(side=ctk.TOP, anchor=ctk.W)

    # Create and pack the button frame and button
    mod_button_frame = ctk.CTkFrame(mod_frame, bg_color="white")
    mod_button_frame.pack(side=ctk.RIGHT)
    mod_button = ctk.CTkButton(mod_button_frame, text="Get", command=lambda: download_mod(mod_data=mod_data, server_info=server_info), fg_color="green")
    mod_button.pack(side=ctk.TOP)

    # Update the canvas to reflect changes
    canvas.update_idletasks()

def callback_display(moddata, canvas, server_info):
    render_mod(mod_data=moddata, canvas=canvas, server_info=server_info)

current_offset = 0
current_search = None
previous_offsets = []
def search_for_mods(server_info, query, canvas, button,offset_to_use=0):
    # log("Searching for mods...")
    loading_label = None  # To keep track of the loading animation label
    mods_g = []
    def search_mods_thread():
        nonlocal loading_label
        global current_offset
        global current_search
        global previous_offsets
        global mods_g
        if(str(current_search) != query):
            current_offset = 0
            current_search = query
            previous_offsets = [0]

        log("Searching for mods...")
        version = server_info.get("gameVersion", "0.0")
        loader = server_info.get("modloader", "null")
        mods,offset = apiv2.search_mods_internal(query=query, version=version, modloader=loader,initial_offset=offset_to_use)
        # mods_g = mods
        for mod in mods:
            render_mod(canvas=canvas, mod_data=mod, server_info=server_info)
        # log(mods)
        button.configure(state=ctk.NORMAL)  # Enable the search button after search completes
        
        # Remove the loading animation
        if loading_label:
            loading_label.destroy()
        current_offset = offset
        previous_offsets.append(offset)
    def animate_loading():
        nonlocal loading_label

        if not loading_label:
            loading_label = ctk.CTkLabel(canvas, text="Loading")
            loading_label.pack()

        def update_animation():
            current_text = loading_label.cget("text")
            if current_text.endswith("..."):
                loading_label.configure(text="Loading")
            else:
                loading_label.configure(text=current_text + ".")

            if search_thread.is_alive():
                canvas.after(500, update_animation)

        update_animation()

    global search_thread
    search_thread = threading.Thread(target=search_mods_thread)
    search_thread.start()
    button.configure(state=ctk.DISABLED)  # Disable the search button while searching

    # Start the loading animation
    animate_loading()
    # search_thread.join()
    # log("render_mod... MODS")
    #THIS
    
def on_close(window):
    # Signal the search thread to stop
    stop_search_thread.set()
    # Wait for the search thread to terminate
    if search_thread.is_alive():
        search_thread.join()
    # Close the window
    window.destroy()


def clear_canvas(canvas):
    # Iterate through all children of the canvas and destroy them
    for widget in canvas.winfo_children():
        widget.destroy()

def find_mod_id(json_path, filename):
    if(json_path == None):
        return None
    try:
        
        with open(json_path, 'r') as file:
            json_data = file.read()
    except FileNotFoundError:
        log(f"Error: JSON file '{json_path}' not found.")
        return None

    try:
        mods = json.loads(json_data)["mods"]
        log("mods = json.loads(json_data)['mods']",mods)
    except json.JSONDecodeError:
        log(f"Error: Invalid JSON format in file '{json_path}'.")
        return None

    for mod in mods:
        log("for mod in mods:",mod)
        for mod_id, mod_file in mod.items():
            decoded_filename = urllib.parse.unquote(mod_file)
            filename = urllib.parse.unquote(filename)
            # log(decoded_filename,filename)
            if filename == decoded_filename:
                return mod_id
    log(f"No mod found for filename '{filename}' in the provided JSON data.")
    return None
def display_mod_files(mod_list_frame,mod_path,json_path):
        for widget in mod_list_frame.winfo_children():
            widget.destroy()
        
        mod_files = [f for f in os.listdir(mod_path) if f.endswith('.jar') or f.endswith('.disabled')]
        log(mod_files)
        for mod in mod_files:
            mod_id = find_mod_id(json_path, mod)
            log("mod_id",mod_id)
            if mod_id != None:
                name = apiv2.id_to_name(mod_id)
            else:
                name = None
            log(mod)
            if(name != None ):
                label = ctk.CTkLabel(mod_list_frame, text=name,text_color="cyan",bg_color=default_color,fg_color=default_color)
            else:
                label = ctk.CTkLabel(mod_list_frame, text=mod,text_color="cyan",bg_color=default_color,fg_color=default_color)
            label.pack(anchor='w', padx=10, pady=2)
def mod_menu(path_in, server_info):
    global current_offset
    global previous_offsets
    window = ctk.CTk()
    window.title("Mod Menu")
    window.geometry("800x600")
    path = server_info.get("path")
    json_path = os.path.join(path,"towtruckconfig.json")
    if(os.path.exists(json_path) == False):
        json_path = None
    # Create the outer frame to hold all other frames
    outer_frame = ctk.CTkFrame(window)
    outer_frame.pack(fill=ctk.BOTH, expand=True)

    # Create the mod list frame first
    mod_list_frame = ctk.CTkFrame(outer_frame, fg_color=default_color)
    mod_list_frame.pack(side=ctk.LEFT, fill=ctk.Y, padx=10, pady=10)

    # Create the canvas and main frame next
    canvas = ctk.CTkCanvas(outer_frame)
    canvas.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)

    scrollbar = ctk.CTkScrollbar(outer_frame, command=canvas.yview)
    scrollbar.pack(side=ctk.RIGHT, fill=ctk.Y)

    canvas.configure(yscrollcommand=scrollbar.set, background=default_color, highlightthickness=0)

    frame = ctk.CTkFrame(canvas, fg_color=default_color)
    canvas.create_window((0, 0), window=frame, anchor=ctk.NW)

    # Create the search frame
    search_frame = ctk.CTkFrame(outer_frame, fg_color=default_color,width=300000)
    search_frame.pack(side=ctk.TOP, fill=ctk.BOTH, padx=10, pady=10)
    def next_mods():
        clear_canvas(frame)
        search_for_mods(server_info, search_bar.get(), frame, search_button,offset_to_use=current_offset)
    def back_mods():
        global previous_offsets
        if(len(previous_offsets) >=3):
            clear_canvas(frame)
            log(previous_offsets)
            index = previous_offsets.index(current_offset)
            offset_use = previous_offsets[index-2]
            # previous_offsets = previous_offsets[:index-2]
            log(offset_use)
            # search_for_mods(server_info, search_bar.get(), frame, search_button,offset_to_use=offset_use)
        
    mod_path = os.path.normpath(os.path.join(path, "mods"))
    search_bar = ctk.CTkEntry(search_frame,width=200)
    search_button = ctk.CTkButton(search_frame, text="Search", command=lambda: search_for_mods(server_info, search_bar.get(), frame, search_button))
    next_page_button = ctk.CTkButton(search_frame, text="Next",command=next_mods)
    back_page_button = ctk.CTkButton(search_frame, text="Back",command=back_mods)
    search_bar.pack(side=ctk.TOP, fill=ctk.X, padx=5, pady=5,expand=True)
    search_button.pack(side=ctk.TOP, padx=5, pady=5)
    next_page_button.pack(side=ctk.TOP, padx=5, pady=5)
    back_page_button.pack(side=ctk.TOP,padx=5, pady=5)


    def on_configure(event):
        canvas.configure(scrollregion=canvas.bbox('all'))

    frame.bind('<Configure>', on_configure)

    # Function to display mod files
    # def display_mod_files():
    #     for widget in mod_list_frame.winfo_children():
    #         widget.destroy()
        
    #     mod_files = [f for f in os.listdir(mod_path) if f.endswith('.jar') or f.endswith('.disabled')]
    #     log(mod_files)
    #     for mod in mod_files:
    #         mod_id = find_mod_id(json_path, mod)
    #         log("mod_id",mod_id)
    #         if mod_id != None:
    #             name = apiv2.id_to_name(mod_id)
    #         else:
    #             name = None
    #         log(mod)
    #         if(name != None ):
    #             label = ctk.CTkLabel(mod_list_frame, text=name,text_color="cyan",bg_color=default_color,fg_color=default_color)
    #         else:
    #             label = ctk.CTkLabel(mod_list_frame, text=mod,text_color="cyan",bg_color=default_color,fg_color=default_color)
    #         label.pack(anchor='w', padx=10, pady=2)

    display_files_thread = threading.Thread(target=display_mod_files,args=(mod_list_frame,mod_path,json_path))
    display_files_thread.start()
    # display_mod_files()

    window.protocol("WM_DELETE_WINDOW", window.destroy)
    window.mainloop()
# setup_logging("./logs/modmenu.log")