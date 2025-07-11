"""
Filename: your_script_name.py
Author: Tristan Kuhn
Date Created: 2024-05-24
License: TOW TRUCK SERVER LICENSE AGREEMENT
Description: This script provides functionalities for creating and configuring game servers. It includes a GUI for adding a new server with customizable options such as server name, description, game version, mod loader, and image.

Usage:
    Import ONLY into main.py

Dependencies:
    - tkinter
    - customtkinter
    - ui.general (custom module)
    - minecraft.minecraft_versions (custom module)
    - minecraft.generation (custom module)
    - server_utils.create_server (custom module)
    - mods.modloader (custom module)
    - libs.CTkScrollableDropdown (custom module)
    - os

Functions:
    - update_seed_label: Updates the label with a random seed.
    - AddServerScreen: Displays a GUI for adding a new server with various options.

Classes:
    None

Notes:
    Ensure that the required custom modules are available in the project.
"""
#TODO Images for servers must be transferred into the servers folders
import tkinter as tk
from tkinter import filedialog
import customtkinter
from ui.general import clear_window
from minecraft.minecraft_versions import minecraft_versions
from minecraft.generation import generate_random_seed
from server_utils.create_server import make_server
from mods.modloader import valid_mod_loaders
from libs.CTkScrollableDropdown import *
import os
import psutil  # to get the total system RAM
from config.ui_config import default_color

file_path = ""

def update_seed_label(seed_label):
    new_seed = generate_random_seed()
    seed_label.configure(text=new_seed)
def AddServerScreen(window):
    total_ram = psutil.virtual_memory().total // (1024 * 1024)
    # clear_window(window)
    # file_path = ""
    # Server Name input
    server_name_label = customtkinter.CTkLabel(window, text="Server Name:",text_color="#00FFFF",bg_color=default_color)
    server_name_label.place(relx=0.3, rely=0.2, anchor=customtkinter.E)
    server_name_entry = customtkinter.CTkEntry(window)
    server_name_entry.place(relx=0.5, rely=0.2, anchor=customtkinter.W)

    # Server Description input
    server_description_label = customtkinter.CTkLabel(window, text="Server Description:",text_color="#00FFFF",bg_color=default_color)
    server_description_label.place(relx=0.3, rely=0.3, anchor=customtkinter.E)
    server_description_entry = customtkinter.CTkEntry(window)
    server_description_entry.place(relx=0.5, rely=0.3, anchor=customtkinter.W)

    # Game Version dropdown
    game_version_label = customtkinter.CTkLabel(window, text="Game Version:",text_color="#00FFFF",bg_color=default_color)
    game_version_label.place(relx=0.3, rely=0.4, anchor=customtkinter.E)
    game_version_combobox = customtkinter.CTkComboBox(window)
    CTkScrollableDropdown(game_version_combobox,values=minecraft_versions,button_color=default_color,text_color="cyan")
    game_version_combobox.set(minecraft_versions[0])
    game_version_combobox.place(relx=0.5, rely=0.4, anchor=customtkinter.W)
    
    modloader_label = customtkinter.CTkLabel(window, text="Mod loader:",text_color="#00FFFF",bg_color=default_color)
    modloader_label.place(relx=0.3, rely=0.5, anchor=customtkinter.E)
    modloader_combobox = customtkinter.CTkComboBox(window)
    CTkScrollableDropdown(modloader_combobox,values=valid_mod_loaders,button_color=default_color,text_color="cyan")
    def update_ram_label(value):
        ram_value_label.configure(text=f"{int(value)} MB")


    modloader_combobox.set(valid_mod_loaders[0])
    modloader_combobox.place(relx=0.5, rely=0.5, anchor=customtkinter.W)
    ram_label = customtkinter.CTkLabel(window, text="Ram:", text_color="#00FFFF",bg_color=default_color)
    ram_label.place(relx=0.3, rely=0.6, anchor=customtkinter.E)

    # Create the label to show the current RAM value
    ram_value_label = customtkinter.CTkLabel(window, text="1 MB",bg_color=default_color,text_color="#00FFFF")
    ram_value_label.place(relx=0.9, rely=0.6, anchor=customtkinter.E)

    # Create the slider to adjust RAM value
    ram_slider = customtkinter.CTkSlider(window, from_=1, to=total_ram, command=update_ram_label)
    ram_slider.place(relx=0.81, rely=0.6, anchor=customtkinter.E)

    # Set the initial value of the slider and update the label
    ram_slider.set(1024)
    update_ram_label(1024)
    # Add Server button
    def add_server():
        name = server_name_entry.get()
        description = server_description_entry.get()
        version = game_version_combobox.get()  # Get the selected version from the combobox
        modloader = modloader_combobox.get()
        ram_slider_val = ram_slider.get()
        ram = f"{int(ram_slider_val)}M"
        make_server(name=name, description=description, version=version,img=file_path,modloader=modloader,ram=ram)  # Call the make_server function with the provided parameters
    
    add_server_button = customtkinter.CTkButton(window, text="Add Server", command=add_server)
    add_server_button.place(relx=0.5, rely=0.7, anchor=customtkinter.CENTER)
    
    # Add Image button
    def add_image():
        global file_path
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        log(os.getcwd(), file_path)
    add_image_button = customtkinter.CTkButton(window, text="Add Image", command=lambda: add_image())

    add_image_button.place(relx=0.5, rely=0.8, anchor=customtkinter.CENTER)