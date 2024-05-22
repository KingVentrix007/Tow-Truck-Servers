
#TODO Images for servers must be transferred into the servers folders
#TODO Redo Path handling, way to much os.chdir() and back and forth, look into better solutions

import tkinter as tk
from tkinter import filedialog
import customtkinter
from ui.general import clear_window
from minecraft.minecraft_versions import minecraft_versions
from minecraft.generation import generate_random_seed
from server_utils.create_server import make_server
from mods.modloader import valid_mod_loaders
file_path = ""

def update_seed_label(seed_label):
    new_seed = generate_random_seed()
    seed_label.configure(text=new_seed)
def AddServerScreen(window):
    clear_window(window)
    # file_path = ""
    # Server Name input
    server_name_label = customtkinter.CTkLabel(window, text="Server Name:")
    server_name_label.place(relx=0.3, rely=0.2, anchor=customtkinter.E)
    server_name_entry = customtkinter.CTkEntry(window)
    server_name_entry.place(relx=0.5, rely=0.2, anchor=customtkinter.W)

    # Server Description input
    server_description_label = customtkinter.CTkLabel(window, text="Server Description:")
    server_description_label.place(relx=0.3, rely=0.3, anchor=customtkinter.E)
    server_description_entry = customtkinter.CTkEntry(window)
    server_description_entry.place(relx=0.5, rely=0.3, anchor=customtkinter.W)

    # Game Version dropdown
    game_version_label = customtkinter.CTkLabel(window, text="Game Version:")
    game_version_label.place(relx=0.3, rely=0.4, anchor=customtkinter.E)
    game_version_combobox = customtkinter.CTkComboBox(window, values=minecraft_versions)
    game_version_combobox.set(minecraft_versions[0])
    game_version_combobox.place(relx=0.5, rely=0.4, anchor=customtkinter.W)
    
    modloader_label = customtkinter.CTkLabel(window, text="Mod loader:")
    modloader_label.place(relx=0.3, rely=0.5, anchor=customtkinter.E)
    modloader_combobox = customtkinter.CTkComboBox(window, values=valid_mod_loaders)
    modloader_combobox.set(valid_mod_loaders[0])
    modloader_combobox.place(relx=0.5, rely=0.5, anchor=customtkinter.W)
    # Seed label and button
    # seed_label = customtkinter.CTkLabel(window, text=generate_random_seed())
    # seed_label.place(relx=0.5, rely=0.6, anchor=customtkinter.W)
    # random_seed_button = customtkinter.CTkButton(window, text="Random Seed", command=lambda: update_seed_label(seed_label))
    # random_seed_button.place(relx=0.8, rely=0.6, anchor=customtkinter.CENTER)

    # Add Server button
    def add_server():
        name = server_name_entry.get()
        description = server_description_entry.get()
        version = game_version_combobox.get()  # Get the selected version from the combobox
        modloader = modloader_combobox.get()
        make_server(name=name, description=description, version=version,img=file_path,modloader=modloader)  # Call the make_server function with the provided parameters
    
    add_server_button = customtkinter.CTkButton(window, text="Add Server", command=add_server)
    add_server_button.place(relx=0.5, rely=0.7, anchor=customtkinter.CENTER)
    
    # Add Image button
    def add_image():
        global file_path
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
    
    add_image_button = customtkinter.CTkButton(window, text="Add Image", command=lambda: add_image())

    add_image_button.place(relx=0.5, rely=0.8, anchor=customtkinter.CENTER)