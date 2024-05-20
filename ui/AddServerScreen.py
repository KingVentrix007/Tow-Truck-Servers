import tkinter as tk
from tkinter import filedialog
import customtkinter
from ui.general import clear_window
from minecraft.minecraft_versions import minecraft_versions
from minecraft.generation import generate_random_seed
from server_utils.create_server import make_server
file_path = ""

def update_seed_label(seed_label):
    new_seed = generate_random_seed()
    seed_label.configure(text=new_seed)
def AddServerScreen(window,parent_screen_function):
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
    
    # Seed label and button
    seed_label = customtkinter.CTkLabel(window, text=generate_random_seed())
    seed_label.place(relx=0.5, rely=0.5, anchor=customtkinter.W)
    random_seed_button = customtkinter.CTkButton(window, text="Random Seed", command=lambda: update_seed_label(seed_label))
    random_seed_button.place(relx=0.8, rely=0.5, anchor=customtkinter.CENTER)

    # Add Server button
    def add_server():
        name = server_name_entry.get()
        description = server_description_entry.get()
        version = game_version_combobox.get()  # Get the selected version from the combobox
        seed = seed_label.cget("text")  # Get the current text of the seed label
        make_server(name, description, version, seed,img=file_path)  # Call the make_server function with the provided parameters
    
    add_server_button = customtkinter.CTkButton(window, text="Add Server", command=add_server)
    add_server_button.place(relx=0.5, rely=0.6, anchor=customtkinter.CENTER)
    
    # Add Image button
    def add_image():
        global file_path
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
    
    add_image_button = customtkinter.CTkButton(window, text="Add Image", command=lambda: add_image())

    add_image_button.place(relx=0.5, rely=0.65, anchor=customtkinter.CENTER)

    # Back button
    back_button = customtkinter.CTkButton(window, text="Back", command=parent_screen_function)
    back_button.place(relx=0.5, rely=0.7, anchor=customtkinter.CENTER)
