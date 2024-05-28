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
from mods.modrinth_api import search_mods
import requests
from io import BytesIO
from PIL import Image, ImageTk
from tkinter import messagebox
import threading
from time import sleep
import tempfile
import shutil
from tkinter import ttk
import mods.modrinth_mods as modrinth_mods
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
    url, deps_url = modrinth_mods.get_download_mod(mod=mod_data, needed_version=server_info.get("gameVersion", "0.0"), modloader=server_info.get("modloader", "null"))
    mod_folder = os.path.normpath(os.path.join(server_info.get("path", None), "mods"))
    os.makedirs(mod_folder, exist_ok=True)

    root = tk.Tk()
    root.title("Download Progress")
    label = ttk.Label(root, text="Downloading mod...")
    label.pack(pady=10)
    progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
    progress.pack(pady=10)

    def download_dependencies():
        for dep_url in deps_url:
            local_dep_filename = os.path.join(mod_folder, os.path.basename(dep_url))
            download_file(dep_url, local_dep_filename, progress, root, label)

        label.config(text="All downloads complete!")
        print("Downloaded all dependencies.")

    def start_download():
        local_filename = os.path.join(mod_folder, os.path.basename(url))
        download_file(url, local_filename, progress, root, label, callback=download_dependencies)
        print("Downloaded mod to %s" % local_filename)
        label.config(text="Mod download complete! Downloading dependencies...")

    threading.Thread(target=start_download).start()
    root.mainloop()

def render_mod(canvas, mod_data, server_info):
    mod_frame = ctk.CTkFrame(canvas, bg_color=default_color)
    mod_frame.pack(side=ctk.TOP, anchor=ctk.W, fill=ctk.X)

    mod_info_frame = ctk.CTkFrame(mod_frame, bg_color=default_color)
    mod_info_frame.pack(side=ctk.LEFT)

    mod_label = ctk.CTkLabel(mod_info_frame, text=mod_data['title'] + " by " + str(mod_data.get("author", "None")), fg_color=default_color, bg_color=default_color)
    mod_label.pack(side=ctk.TOP, anchor=ctk.W)

    mod_button_frame = ctk.CTkFrame(mod_frame, bg_color="white")
    mod_button_frame.pack(side=ctk.RIGHT)
    # mod_url = modrinth_mods.get_download_url(mod=mod_data,needed_version=server_info.get("gameVersion", "0.0"),modloader=server_info.get("modloader", "null"))
    mod_button = ctk.CTkButton(mod_button_frame, text="Get", command=lambda: download_mod(mod_data=mod_data, server_info=server_info), fg_color="green")
    mod_button.pack(side=ctk.TOP)

    canvas.update_idletasks()
    canvas_width = canvas.winfo_width()
    mod_frame.configure(width=canvas_width)

def callback_display(moddata, canvas, server_info):
    render_mod(mod_data=moddata, canvas=canvas, server_info=server_info)

def search_for_mods(server_info, query, canvas, button):
    print("Searching for mods...")

    def search_mods_thread():
        version = server_info.get("gameVersion", "0.0")
        loader = server_info.get("modloader", "null")
        mods = modrinth_mods.search_mods(query=query,version=version,modloader=loader)#search_mods(query=query, game_version=version, mod_loader=loader, callback=callback_display, canvas=canvas, server_data=server_info)
        for mod in mods:
            render_mod(canvas=canvas, mod_data=mod,server_info=server_info)
        print(mods)
        button.configure(state=ctk.NORMAL)  # Enable the search button after search completes

    global search_thread
    search_thread = threading.Thread(target=search_mods_thread)
    search_thread.start()
    button.configure(state=ctk.DISABLED)  # Disable the search button while searching

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
