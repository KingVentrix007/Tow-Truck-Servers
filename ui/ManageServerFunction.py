import tkinter as tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
import customtkinter as ctk
from ui.general import clear_window
from server_utils.server_manager import get_all_servers, load_properties, del_server
from ui.settings import edit_properties_window
from ui.ModMenu import mod_menu
from server_utils.server import run_server  # Ensure this function returns the process
from file_utils.path_mangment import adjust_path
import os

current_Server_data = ""
process = None  # Ensure process is a global variable

def ManageServerFunction(window, parent_screen_function):
    clear_window(window)

    servers = get_all_servers()
    
    tabview = ctk.CTkTabview(window)
    tabview.pack(expand=1, fill='both')

    def create_server_tab(tabview, server_info):
        global process  # Ensure process is global

        def open_settings():
            adjust_path()
            path = server_info.get('path', "/fake/")
            properties_file = os.path.join(path, "server.properties")
            properties_file = os.path.normpath(properties_file)
            print("properties_file ==", properties_file)
            if os.path.exists(properties_file):
                properties = load_properties(properties_file)
                global current_Server_data
                current_Server_data = server_info
                edit_properties_window(properties, properties_file, server_tab, back_tab)
            else:
                messagebox.showerror("Error", f"server.properties file not found at {properties_file}")

        def send_command():
            global process  # Ensure process is global
            command = command_entry.get()
            print("command")
            print("Process == ", process)
            print("process.stdin == ", process.stdin if process else None)
            if process and process.stdin:
                print("command is being run\n")
                process.stdin.write(command + "\n")
                process.stdin.flush()
            else:
                messagebox.showerror("Error", "Process is not running")

        def del_server_callback():
            del_server(server_info.get('displayName', "Unnamed Server"))

        def run_server_callback():
            global process  # Ensure process is global
            process = run_server(server_info, text_widget)
            if process is None:
                messagebox.showerror("Error", "Failed to start the server")
            else:
                print("Server process started")

        tab_name = server_info.get('displayName', "Server")
        server_tab = tabview.add(tab_name)

        def back_tab():
            create_server_tab(tabview, current_Server_data)

        # Create a frame for the top menu bar
        menu_bar = ctk.CTkFrame(server_tab)
        menu_bar.pack(side=tk.TOP, fill=tk.X)

        delete_button = ctk.CTkButton(menu_bar, text="Delete", command=del_server_callback)
        delete_button.pack(side=tk.LEFT, padx=5, pady=5)
        run_button = ctk.CTkButton(menu_bar, text="Run", command=run_server_callback)
        run_button.pack(side=tk.LEFT, padx=5, pady=5)

        settings_button = ctk.CTkButton(menu_bar, text="Settings", command=open_settings)
        settings_button.pack(side=tk.LEFT, padx=5, pady=5)

        mod_btn = ctk.CTkButton(menu_bar, text="Mod Menu", command=lambda: mod_menu(server_info.get('path', 'null')))
        mod_btn.pack(side=tk.LEFT, padx=5, pady=5)

        text_widget = ScrolledText(server_tab, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True)

        command_entry = ctk.CTkEntry(server_tab)
        command_entry.pack(fill=tk.X, pady=5)

        send_button = ctk.CTkButton(server_tab, text="Send Command", command=send_command)
        send_button.pack(pady=5)

    for server in servers:
        create_server_tab(tabview, server)

    back_button = ctk.CTkButton(window, text="Back", command=parent_screen_function)
    back_button.pack(pady=10)