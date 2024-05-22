import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
import os

made_home_screen = False
home_screen_ext = None

def HomeScreen(tab_view, servers):
    global made_home_screen, home_screen_ext
    if not made_home_screen:
        home_screen = ctk.CTkFrame(tab_view)
        home_screen.pack(fill="both", expand=True)
        home_screen_ext = home_screen
        made_home_screen = True
        display_servers(home_screen, servers[:5])
    else:
        home_screen = home_screen_ext

def display_servers(frame, servers):
    for i, server in enumerate(servers):
        server_frame = ctk.CTkFrame(frame)
        server_frame.pack(fill="x", padx=10, pady=5)

        # Check if image path is valid, otherwise use default image
        if server["modloader"] == "forge":
            backup_path = "./img/forge.png"
        elif server["modloader"] == "fabric":
            backup_path = "./img/fabric.png"
        else:
            backup_path = "./img/package.png"
        img_path = server["image"] if os.path.isfile(server["image"]) else backup_path

        # Load and resize image
        img = Image.open(img_path)
        img = img.resize((50, 50))
        img = ImageTk.PhotoImage(img)
        img_label = ctk.CTkLabel(server_frame, image=img, text="")
        img_label.image = img  # Keep a reference to avoid garbage collection
        img_label.pack()

        # Display name and version
        name_version_label = ctk.CTkLabel(server_frame, text=f"{server['displayName']} - {server['gameVersion']}", font=("Arial", 16))
        name_version_label.pack()

        # Add button
        button = ctk.CTkButton(server_frame, text="Launch")
        button.pack()

        # Display description
        description_label = ctk.CTkLabel(server_frame, text=server['description'], font=("Arial", 12))
        description_label.pack()

        # Display java version and ram in small grey letters
        details_label = ctk.CTkLabel(server_frame, text=f"Java: {server['javaVersion']} | RAM: {server['ram']}", font=("Arial", 10))
        details_label.pack()