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
from io import BytesIO
from PIL import Image, ImageTk
from tkinter import messagebox
import threading
from time import sleep
import tempfile
import shutil
from tkinter import ttk
import mods.apiv2 as apiv2
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

def download_mod(mod_data, server_info):
    server_folder = server_info.get("path")
    config_path = os.path.join(server_folder, 'towtruckconfig.json')
    mod_id = mod_data["project_id"]
    
    # Ensure the configuration file exists
    if not os.path.exists(config_path):
        with open(config_path, 'w') as config_file:
            json.dump({"mods": []}, config_file)

    # Load the configuration file
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)
    
    # Check if the main mod is already installed
    if mod_id in config["mods"]:
        print(f"Mod {mod_id} is already installed, skipping download.")
        return
    
    def show_waiting_window():
        waiting_root = tk.Toplevel()
        waiting_root.title("Please Wait")
        name = mod_data.get("title")
        waiting_label = ttk.Label(waiting_root, text=f"Searching for mod URLs for {name}...")
        waiting_label.pack(pady=20, padx=20)
        return waiting_root

    def close_waiting_window(waiting_root):
        if waiting_root:
            waiting_root.destroy()

    def get_mod_urls():
        mod = apiv2.get_download_urls(mod_data["project_id"], server_info.get("gameVersion", "0.0"), server_info.get("modloader", "null"))[0]
        return mod

    waiting_window = show_waiting_window()

    def fetch_and_download():
        nonlocal waiting_window

        # Get the mod URLs
        urls = get_mod_urls()
        url = urls["url"]
        dependencies = urls["dependencies"]
        close_waiting_window(waiting_window)
        mod_folder = os.path.normpath(os.path.join(server_info.get("path", None), "mods"))
        os.makedirs(mod_folder, exist_ok=True)

        root = tk.Tk()
        root.title("Download Progress")
        mod_name = mod_data["title"]
        label = ttk.Label(root, text=f"Downloading mod {mod_name}...")
        label.pack(pady=10)
        progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
        progress.pack(pady=10)

        def download_dependencies():
            label.config(text="Mod download complete! Downloading dependencies...")
            for dep in dependencies:
                dep_id = dep["id"]
                dep_url = dep["url"]
                if dep_id not in config["mods"]:
                    if dep_url is not None:
                        local_dep_filename = os.path.join(mod_folder, os.path.basename(dep_url))
                        download_file(dep_url, local_dep_filename, progress, root, label)
                        config["mods"].append(dep_id)  # Add the dependency ID to the config
                        with open(config_path, 'w') as config_file:
                            json.dump(config, config_file, indent=4)
                else:
                    print(f"Dependency {dep_id} already exists, skipping download.")

            label.config(text="All downloads complete!")
            print("Downloaded all dependencies.")

        def start_download():
            local_filename = os.path.join(mod_folder, os.path.basename(url))
            download_file(url, local_filename, progress, root, label, callback=download_dependencies)
            config["mods"].append(mod_id)  # Add the main mod ID to the config
            with open(config_path, 'w') as config_file:
                json.dump(config, config_file, indent=4)
            print(f"Downloaded mod to {local_filename}")

        threading.Thread(target=start_download).start()
        root.mainloop()

    # Fetch mod URLs and start the download process in a separate thread
    threading.Thread(target=fetch_and_download).start()

def render_mod(canvas, mod_data, server_info):
    mod_frame = ctk.CTkFrame(canvas, bg_color=default_color)
    mod_frame.pack(side=ctk.TOP, anchor=ctk.W, fill=ctk.X)

    mod_info_frame = ctk.CTkFrame(mod_frame, bg_color=default_color)
    mod_info_frame.pack(side=ctk.LEFT)

    mod_label = ctk.CTkLabel(mod_info_frame, text=mod_data['title'] + " by " + str(mod_data.get("author", "None")), fg_color=default_color, bg_color=default_color)
    mod_label.pack(side=ctk.TOP, anchor=ctk.W)

    mod_button_frame = ctk.CTkFrame(mod_frame, bg_color="white")
    mod_button_frame.pack(side=ctk.RIGHT)
    mod_button = ctk.CTkButton(mod_button_frame, text="Get", command=lambda: download_mod(mod_data=mod_data, server_info=server_info), fg_color="green")
    mod_button.pack(side=ctk.TOP)

    canvas.update_idletasks()
    canvas_width = canvas.winfo_width()
    mod_frame.configure(width=canvas_width)

def callback_display(moddata, canvas, server_info):
    render_mod(mod_data=moddata, canvas=canvas, server_info=server_info)

def search_for_mods(server_info, query, canvas, button):
    # print("Searching for mods...")
    
    loading_label = None  # To keep track of the loading animation label

    def search_mods_thread():
        nonlocal loading_label
        print("Searching for mods...")
        version = server_info.get("gameVersion", "0.0")
        loader = server_info.get("modloader", "null")
        mods = apiv2.search_mods(query=query, version=version, modloader=loader)
        for mod in mods:
            render_mod(canvas=canvas, mod_data=mod, server_info=server_info)
        print(mods)
        button.configure(state=ctk.NORMAL)  # Enable the search button after search completes
        
        # Remove the loading animation
        if loading_label:
            loading_label.destroy()

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
def on_close(window):
    # Signal the search thread to stop
    stop_search_thread.set()
    # Wait for the search thread to terminate
    if search_thread.is_alive():
        search_thread.join()
    # Close the window
    window.destroy()

def mod_menu(path, server_info):
    window = ctk.CTk()
    window.title("Mod Menu")
    window.geometry("800x600")

    canvas = ctk.CTkCanvas(window)
    canvas.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)

    scrollbar = ctk.CTkScrollbar(window, command=canvas.yview)
    scrollbar.pack(side=ctk.RIGHT, fill=ctk.Y)

    canvas.configure(yscrollcommand=scrollbar.set, background=default_color, highlightthickness=0)

    frame = ctk.CTkFrame(canvas, fg_color=default_color)
    canvas.create_window((0, 0), window=frame, anchor=ctk.NW)
    search_frame = ctk.CTkFrame(canvas, fg_color=default_color)
    canvas.create_window((0, 0), window=search_frame, anchor=ctk.NW)
    mod_path = os.path.normpath(os.path.join(path, "mods"))
    search_bar = ctk.CTkEntry(search_frame)
    search_button = ctk.CTkButton(search_frame, text="Search", command=lambda: search_for_mods(server_info, search_bar.get(), frame, search_button))

    def on_configure(event):
        canvas.configure(scrollregion=canvas.bbox('all'))

    frame.bind('<Configure>', on_configure)

    frame.pack(side=ctk.LEFT, fill=ctk.Y)
    search_frame.pack(side=ctk.LEFT, fill=ctk.Y)
    search_bar.pack(side=ctk.TOP, fill=ctk.X)
    search_button.pack(side=ctk.TOP, fill=ctk.X)

    window.protocol("WM_DELETE_WINDOW", lambda: on_close(window))
    window.mainloop()
