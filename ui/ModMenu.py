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
# Define a function to download an image to a temporary directory
def download_mod(url, server_info):
    # Get the mods folder path from the server_info dictionary
    mod_folder = os.path.normpath(os.path.join(server_info.get("path", None), "mods"))

    # Ensure the mods folder exists
    os.makedirs(mod_folder, exist_ok=True)

    # Define the local file path for the downloaded mod
    local_filename = os.path.join(mod_folder, os.path.basename(url))

    # Create a Tkinter window
    root = tk.Tk()
    root.title("Download Progress")

    # Create a label
    label = ttk.Label(root, text="Downloading mod...")
    label.pack(pady=10)

    # Create a progress bar
    progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
    progress.pack(pady=10)

    # Function to download the file and update the progress bar
    def start_download():
        with requests.get(url, stream=True) as response:
            response.raise_for_status()  # Raise an error for bad status codes
            total_length = int(response.headers.get('content-length', 0))
            downloaded = 0

            with open(local_filename, 'wb') as out_file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  # filter out keep-alive new chunks
                        out_file.write(chunk)
                        downloaded += len(chunk)
                        progress["value"] = (downloaded / total_length) * 100
                        root.update_idletasks()

        print("Downloaded mod to %s" % local_filename)
        label.config(text="Download complete!")

    # Start the download in a separate thread to avoid blocking the GUI
    import threading
    threading.Thread(target=start_download).start()

    # Start the Tkinter event loop
    root.mainloop()

def render_mod(canvas, mod_data,server_info):
    mod_frame = ctk.CTkFrame(canvas, bg_color=default_color)
    mod_frame.pack(side=ctk.TOP, anchor=ctk.W, fill=ctk.X)

    mod_info_frame = ctk.CTkFrame(mod_frame, bg_color=default_color)
    mod_info_frame.pack(side=ctk.LEFT)

    mod_label = ctk.CTkLabel(mod_info_frame, text=mod_data['title'] + " by " + str(mod_data.get("user", "None")), fg_color=default_color, bg_color=default_color)
    mod_label.pack(side=ctk.TOP, anchor=ctk.W)

    # icon_url = mod_data.get('icon', '')  # Assuming 'icon' key contains the URL of the icon
    # icon_label = ctk.CTkLabel(mod_info_frame, bg_color=default_color)

    # if icon_url:
    #     try:
    #         # Download the image
    #         image_path = download_image(icon_url)
    #         if image_path:
    #             # Load the downloaded image
    #             image = Image.open(image_path)
    #             image = image.resize((50, 50))  # Resize the image to 50x50

    #             # Convert PIL.Image to Tkinter PhotoImage
    #             photo = ImageTk.PhotoImage(image)

    #             # Use the image option of the label to display the image
    #             icon_label.configure(image=photo)
    #             icon_label.image = photo  # Maintain a reference to prevent garbage collection

    #             print("Image loaded for:", icon_url)
    #         else:
    #             print("Failed to download image:", icon_url)
    #     except Exception as e:
    #         print("Error fetching icon:", e)
                # icon_label.pack(side=ctk.TOP, anchor=ctk.W)

    mod_button_frame = ctk.CTkFrame(mod_frame, bg_color="white")
    mod_button_frame.pack(side=ctk.RIGHT)

    mod_button = ctk.CTkButton(mod_button_frame, text="Get", command=lambda: download_mod(mod_data['url'],server_info), fg_color="green")
    mod_button.pack(side=ctk.TOP)

    canvas.update_idletasks()
    canvas_width = canvas.winfo_width()
    mod_frame.configure(width=canvas_width)
def callback_display(moddata,canvas,server_info):
    render_mod(mod_data=moddata,canvas=canvas,server_info=server_info)
    # pass

def search_for_mods(server_info, query, canvas, button):
    print("Searching for mods...")

    def search_mods_thread():
        version = server_info.get("gameVersion", "0.0")
        loader = server_info.get("modloader", "null")
        mods = search_mods(query=query, game_version=version, mod_loader=loader,callback=callback_display,canvas=canvas,server_data=server_info)
        print(mods)
        # for mod_data in mods:
        #     render_mod(canvas, mod_data,server_info)
        #     canvas.update_idletasks()  # Update the canvas after rendering each mod

        button.configure(state=ctk.NORMAL)  # Enable the search button after search completes

    search_thread = threading.Thread(target=search_mods_thread)
    search_thread.start()
    button.configure(state=ctk.DISABLED)  # Disable the search button while searching
def mod_menu(path,server_info):

    window = ctk.CTk()
    window.title("Mod Menu")
    window.geometry("800x600")

    canvas = ctk.CTkCanvas(window)
    canvas.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)

    scrollbar = ctk.CTkScrollbar(window, command=canvas.yview)
    scrollbar.pack(side=ctk.RIGHT, fill=ctk.Y)

    canvas.configure(yscrollcommand=scrollbar.set,background=default_color,highlightthickness=0)

    frame = ctk.CTkFrame(canvas,fg_color=default_color)
    canvas.create_window((0, 0), window=frame, anchor=ctk.NW)
    search_frame = ctk.CTkFrame(canvas,fg_color=default_color)
    canvas.create_window((0, 0), window=search_frame, anchor=ctk.NW)
    mod_path = os.path.normpath(os.path.join(path, "mods"))
    search_bar = ctk.CTkEntry(search_frame)
    search_button = ctk.CTkButton(search_frame, text="Search",command=lambda:search_for_mods(server_info,search_bar.get(),frame,search_button))
    # Function to toggle mod activation
    # def toggle_mod(mod_name, toggle_var, toggle_button):
    #     current_extension = ".jar"
    #     new_extension = ".disabled"
    #     text_color = "gray"
    #     mod_file_path = os.path.normpath(os.path.join(mod_path, mod_name + current_extension))
    #     new_file_path = os.path.normpath(os.path.join(mod_path, mod_name + new_extension))

    #     if toggle_var.get() == 1:  # If mod is currently enabled
    #         if os.path.exists(mod_file_path):
    #             os.rename(mod_file_path, new_file_path)
    #             toggle_button.configure(text="Disabled", fg_color=text_color)
    #             toggle_var.set(0)
    #             print(f"Toggled {mod_file_path} to {new_file_path}")
    #         else:
    #             print(f"Error: File {mod_file_path} does not exist")
    #     else:  # If mod is currently disabled
    #         if os.path.exists(new_file_path):
    #             os.rename(new_file_path, mod_file_path)
    #             toggle_button.configure(text="Enabled", fg_color="blue")
    #             toggle_var.set(1)
    #             print(f"Toggled {new_file_path} to {mod_file_path}")
    #         else:
    #             print(f"Error: File {new_file_path} does not exist")
    # List all files in the mods directory
    # mod_files = [file for file in os.listdir(mod_path) if file.endswith('.jar') or file.endswith('.disabled')]

    # Create a label and toggle switch for each mod
    # toggle_vars = {}
    # for mod_file in mod_files:
    #     mod_name, mod_extension = os.path.splitext(mod_file)
    #     is_enabled = mod_extension == '.jar'
    #     toggle_vars[mod_name] = ctk.IntVar(value=1 if is_enabled else 0)

    #     mod_frame = ctk.CTkFrame(frame)
    #     mod_frame.pack(side=ctk.TOP, anchor=ctk.W, fill=ctk.X)

    #     mod_label = ctk.CTkLabel(mod_frame, text=mod_name + "  ")
    #     mod_label.pack(side=ctk.LEFT)

    #     # Ensure the correct value of mod_name is captured in the lambda
    #     def create_toggle_callback(mod_name=mod_name, toggle_var=toggle_vars[mod_name]):
    #         return lambda: toggle_mod(mod_name, toggle_var, mod_button)

    #     # Check if the .disabled file exists to set the initial state correctly
    #     initial_state = "Enabled" if is_enabled else "Disabled"
    #     if os.path.exists(os.path.join(mod_path, mod_name + ".disabled")):
    #         initial_state = "Disabled"  # If the .disabled file exists, set initial state to "Disabled"

    #     text_color = "blue" if is_enabled else "gray"
    #     mod_button = ctk.CTkButton(
    #         mod_frame,
    #         text=initial_state,  # Set initial state text
    #         command=create_toggle_callback(),
    #         fg_color=text_color
    #     )
    #     mod_button.pack(side=ctk.RIGHT)


    def on_configure(event):
        canvas.configure(scrollregion=canvas.bbox('all'))

    frame.bind('<Configure>', on_configure)

    # Position the frame on the left side of the window
    frame.pack(side=ctk.LEFT, fill=ctk.Y)
    search_frame.pack(side=ctk.LEFT, fill=ctk.Y)
    search_bar.pack(side=ctk.TOP, fill=ctk.X)
    search_button.pack(side=ctk.TOP,fill=ctk.X)
    window.mainloop()