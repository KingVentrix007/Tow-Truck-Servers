"""
Filename: HomeScreen.py
Author: Tristan Kuhn
Date: 2024-05-24
License: TOW TRUCK SERVER LICENSE AGREEMENT

Usage:
    HomeScreen.py is a GUI module for Tow Truck Server

Dependencies:
    customtkinter
    PIL
    CTkMessagebox
Functions:
    - HomeScreen: Entry point for program, creates tab window.
    - display_servers: Displays a list of servers
    - manage_server: Gos to the server manager-

Classes:
    - None

Notes:
    Throws UserWarning concerning images, 
    Do not remove 'import tkinter as tk' 
    
"""
import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
import os
from CTkMessagebox import CTkMessagebox
from ui.ManageServerFunction import ManageServerFunction
from config.ui_config import default_color

made_home_screen = False
home_screen_ext = None
def HomeScreen(tab_view, servers,manage_server_tab):
    global made_home_screen, home_screen_ext
    if not made_home_screen:
        home_screen = ctk.CTkFrame(tab_view,bg_color=default_color,fg_color=default_color)
        home_screen.pack(fill="both", expand=True)
        home_screen_ext = home_screen
        made_home_screen = True
        display_servers(home_screen, servers[:5],manage_server_tab)
    else:
        # Prevents a new window from being created
        pass
        
def manage_server(server_name,servers,manage_server_tab):
    log("Handling server: " + server_name)
    log("Server data: ", servers)
    log(manage_server_tab)
    # CTkMessagebox(title="Error",message="Currently this function is not supported",icon="cancel",sound="./assets/sound/error.mp3")
    manage_server_tab()
    # ManageServerFunction(manage_server_tab)
def display_servers(frame, servers,manage_server_tab):
    for i, server in enumerate(servers):
        server_frame = ctk.CTkFrame(frame,fg_color="#2b2b22")
        server_frame.grid(row=0, column=i, padx=10, pady=5)

        if server["modloader"] == "forge":
            backup_path = "./assets/images/forge.png"
        elif server["modloader"] == "fabric":
            backup_path = "./assets/images/fabric.png"
        else:
            backup_path = "./assets/images/package.png"
        img_path = server["image"] if os.path.isfile(server["image"]) else backup_path

        # Load and resize image
        img = Image.open(img_path)
        img = img.resize((50, 50))
        img = ImageTk.PhotoImage(img)
        img_label = ctk.CTkLabel(server_frame, image=img, text="")
        img_label.image = img  # Keep a reference to avoid garbage collection
        img_label.pack()

        # Display name and version
        name_version_label = ctk.CTkLabel(server_frame, text_color="cyan",text=f"{server['displayName']}", font=("Arial", 16))
        name_version_label.pack()

        # Add button
        # button = ctk.CTkButton(server_frame, text="Manage")
        button = ctk.CTkButton(server_frame, text="Manage", command=lambda server_name=server['displayName'], server_data=server: manage_server(server_name, server_data,manage_server_tab))
        button.pack()

        # Display description
        modloader = ctk.CTkLabel(server_frame, text=f"{server['modloader']} {server['gameVersion']}", font=("Arial", 12))
        modloader.pack()
