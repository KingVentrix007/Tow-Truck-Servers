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
def mod_menu(path):

    window = ctk.CTk()
    window.title("Mod Menu")
    window.geometry("800x600")

    canvas = ctk.CTkCanvas(window)
    canvas.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)

    scrollbar = ctk.CTkScrollbar(window, command=canvas.yview)
    scrollbar.pack(side=ctk.RIGHT, fill=ctk.Y)

    canvas.configure(yscrollcommand=scrollbar.set,background="#2b2b2b",highlightthickness=0)

    frame = ctk.CTkFrame(canvas)
    canvas.create_window((0, 0), window=frame, anchor=ctk.NW)

    mod_path = os.path.normpath(os.path.join(path, "mods"))

    # Function to toggle mod activation
    def toggle_mod(mod_name, toggle_var, toggle_button):
        current_extension = ".jar"
        new_extension = ".disabled"
        text_color = "gray"
        mod_file_path = os.path.normpath(os.path.join(mod_path, mod_name + current_extension))
        new_file_path = os.path.normpath(os.path.join(mod_path, mod_name + new_extension))

        if toggle_var.get() == 1:  # If mod is currently enabled
            if os.path.exists(mod_file_path):
                os.rename(mod_file_path, new_file_path)
                toggle_button.configure(text="Disabled", fg_color=text_color)
                toggle_var.set(0)
                print(f"Toggled {mod_file_path} to {new_file_path}")
            else:
                print(f"Error: File {mod_file_path} does not exist")
        else:  # If mod is currently disabled
            if os.path.exists(new_file_path):
                os.rename(new_file_path, mod_file_path)
                toggle_button.configure(text="Enabled", fg_color="blue")
                toggle_var.set(1)
                print(f"Toggled {new_file_path} to {mod_file_path}")
            else:
                print(f"Error: File {new_file_path} does not exist")
    # List all files in the mods directory
    mod_files = [file for file in os.listdir(mod_path) if file.endswith('.jar') or file.endswith('.disabled')]

    # Create a label and toggle switch for each mod
    toggle_vars = {}
    for mod_file in mod_files:
        mod_name, mod_extension = os.path.splitext(mod_file)
        is_enabled = mod_extension == '.jar'
        toggle_vars[mod_name] = ctk.IntVar(value=1 if is_enabled else 0)

        mod_frame = ctk.CTkFrame(frame)
        mod_frame.pack(side=ctk.TOP, anchor=ctk.W, fill=ctk.X)

        mod_label = ctk.CTkLabel(mod_frame, text=mod_name + "  ")
        mod_label.pack(side=ctk.LEFT)

        # Ensure the correct value of mod_name is captured in the lambda
        def create_toggle_callback(mod_name=mod_name, toggle_var=toggle_vars[mod_name]):
            return lambda: toggle_mod(mod_name, toggle_var, mod_button)

        # Check if the .disabled file exists to set the initial state correctly
        initial_state = "Enabled" if is_enabled else "Disabled"
        if os.path.exists(os.path.join(mod_path, mod_name + ".disabled")):
            initial_state = "Disabled"  # If the .disabled file exists, set initial state to "Disabled"

        text_color = "blue" if is_enabled else "gray"
        mod_button = ctk.CTkButton(
            mod_frame,
            text=initial_state,  # Set initial state text
            command=create_toggle_callback(),
            fg_color=text_color
        )
        mod_button.pack(side=ctk.RIGHT)


    def on_configure(event):
        canvas.configure(scrollregion=canvas.bbox('all'))

    frame.bind('<Configure>', on_configure)

    # Position the frame on the left side of the window
    frame.pack(side=ctk.LEFT, fill=ctk.Y)
    window.mainloop()