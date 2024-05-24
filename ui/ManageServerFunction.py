"""
Filename: ManageServerFunction.py
Author: Tristan Kuhn
Date Created: 2024-05-24
License: TOW TRUCK SERVER LICENSE AGREEMENT
Description: This script provides functions for managing game servers including running, stopping, deleting, and accessing server settings. It includes GUI components for displaying server output, sending commands to servers, and interacting with server settings.

Usage:
    Import ONLY into main.py

Dependencies:
    - tkinter
    - tkinter.scrolledtext
    - customtkinter
    - server_utils.server_manager (custom module)
    - ui.settings (custom module)
    - ui.ModMenu (custom module)
    - server_utils.server (custom module)
    - file_utils.path_management (custom module)
    - config.globals (custom module)
    - config.errors (custom module)
    - os

Functions:
    - open_settings: Opens the settings window for a specified server.
    - send_command: Sends a command to the specified server.
    - run_server_callback: Callback function to run a server.
    - on_server_complete: Callback function called when a server stops running.
    - del_server_callback: Callback function to delete a server.
    - create_server_tab: Creates a new tab for a server in the GUI.
    - ManageServerFunction: Main function for managing game servers.

Classes:
    None

Notes:
    - This script relies on various custom modules for server management and GUI components.
"""
import tkinter as tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
import customtkinter as ctk
from server_utils.server_manager import get_all_servers, load_properties, del_server
from ui.settings import edit_properties_window
from ui.ModMenu import mod_menu
from server_utils.server import run_server  # Ensure this function returns the process
from file_utils.path_management import adjust_path
from config.globals import is_server_running,set_server_running,set_server_stopped,default_server_name
from config.errors import err_code_process_closed
import os

current_Server_data = ""
processes = {}  # Dictionary to store server processes
server_states = {}  # Dictionary to store server states including text content
made_servers = []
made_tab_view = False
global tabview
created_tabs = {}  # Dictionary to store created tabs by their names
def open_settings(server_info):
            adjust_path()
            path = server_info.get('path', "/fake/")
            properties_file = os.path.join(path, "server.properties")
            properties_file = os.path.normpath(properties_file)
            print("properties_file ==", properties_file)
            if os.path.exists(properties_file):
                properties = load_properties(properties_file)
                global current_Server_data
                current_Server_data = server_info
                edit_properties_window(properties, properties_file)
            else:
                messagebox.showerror("Error", f"server.properties file not found at {properties_file}")
def send_command(command,server_name):
            if server_name in processes and processes[server_name] is not None:
                # Retrieve the correct process based on the currently selected tab
                current_process = processes[server_name]
                print(f"Sending {command} to {current_process} pid {current_process.pid}")
                current_process.stdin.write(command + "\n")
                current_process.stdin.flush()
            else:
                messagebox.showerror("Error", "Process is not running")

def run_server_callback(text_widget,server_info,on_server_complete):
            server_name = server_info.get("displayName", "server")
            
            if(is_server_running() == True):
                messagebox.showerror("Error", f"Running multiple servers simultaneously is not supported. See {err_code_process_closed} for more details.")
            else:
                set_server_running()
                text_widget.delete('1.0',tk.END)
                if server_name not in processes or processes[server_name] is None:
                    # Store the server process in the dictionary
                    processes[server_name] = run_server(server_info, text_widget,on_server_complete)
                    if processes[server_name] is None:
                        messagebox.showerror("Error", "Failed to start the server")
                    else:
                        print(f"Server {server_name} started with pid ",processes[server_name].pid)
def on_server_complete(server_data,server_output):
            int_server_name = server_data.get('displayName', default_server_name)
            print(f"Server {int_server_name} pid {processes[int_server_name].pid} is being stopped")
            pid = processes[int_server_name].pid
            processes.pop(int_server_name)
            print(f'Server {int_server_name} has been stopped: PID {pid}')
            print("Server",int_server_name,int_server_name not in processes)
            set_server_stopped()
            server_output.insert(tk.END, "Server has stopped, you are free to start another server or edit the configuration of this server. Keep Trucking ")
def del_server_callback(server_info):
            messagebox.showerror("Error", "Until further notice, this feature is disabled")
            return -1
            # This is temporary
            server_name = server_info.get('displayName', default_server_name)
            del_server(server_info.get('displayName', default_server_name))
            if server_name in processes:
                del processes[server_name]
            if server_name in server_states:
                del server_states[server_name]
            tabview.delete(created_tabs[server_name])
            del created_tabs[server_name]
def create_server_tab(tabview, server_info):
        global  created_tabs
        server_name = server_info.get('displayName', default_server_name)
        
        # Check if tab with the same name already exists
        if server_name in created_tabs:
            tabview.select(created_tabs[server_name])  # Focus on existing tab
            return
        
        

        

        
        

        
        
        tab_name = server_info.get('displayName', default_server_name)
        server_tab = tabview.add(tab_name)
        created_tabs[server_name] = server_tab  # Add the created tab to the dictionary
        # Create a frame for the top menu bar
        menu_bar = ctk.CTkFrame(server_tab)
        menu_bar.pack(side=tk.TOP, fill=tk.X)

        delete_button = ctk.CTkButton(menu_bar, text="Delete", command=lambda:del_server_callback(server_info))
        delete_button.pack(side=tk.LEFT, padx=5, pady=5)
        run_button = ctk.CTkButton(menu_bar, text="Run", command=lambda:run_server_callback(text_widget,server_info,on_server_complete))
        run_button.pack(side=tk.LEFT, padx=5, pady=5)

        settings_button = ctk.CTkButton(menu_bar, text="Settings", command=lambda: open_settings(server_info))
        settings_button.pack(side=tk.LEFT, padx=5, pady=5)

        mod_btn = ctk.CTkButton(menu_bar, text="Mod Menu", command=lambda: mod_menu(server_info.get('path', 'null')))
        mod_btn.pack(side=tk.LEFT, padx=5, pady=5)

        text_widget = ScrolledText(server_tab, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True)

        if server_name in server_states:
            text_widget.insert(tk.END, server_states[server_name]['text'])
            if server_states[server_name]['is_running']:
                run_server_callback(text_widget,server_info,on_server_complete)

        command_entry = ctk.CTkEntry(server_tab)
        command_entry.pack(fill=tk.X, pady=5)

        send_button = ctk.CTkButton(server_tab, text="Send Command", command=lambda:send_command(command_entry.get(),server_name))
        send_button.pack(pady=5)
def ManageServerFunction(window):
    # clear_window(window)
    global made_tab_view
    global tabview
    servers = get_all_servers()
    if made_tab_view == False:
        tabview_internal = ctk.CTkTabview(window)
        tabview_internal.pack(expand=1, fill='both')
        tabview = tabview_internal
    made_tab_view = True
    

    for server in servers:
        if server in made_servers:
            # if server is already created, don't create it again
            pass
        else:
            made_servers.append(server)
            create_server_tab(tabview, server)

#Server process started 18004
#18004
#Server process started 18004