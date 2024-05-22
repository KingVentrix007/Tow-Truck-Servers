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
processes = {}  # Dictionary to store server processes
server_states = {}  # Dictionary to store server states including text content
made_servers = []
made_tab_view = False
global tabview
def ManageServerFunction(window, parent_screen_function):
    # clear_window(window)
    global made_tab_view
    global tabview
    servers = get_all_servers()
    if(made_tab_view == False):
        tabview_internal = ctk.CTkTabview(window)
        tabview_internal.pack(expand=1, fill='both')
        tabview = tabview_internal
    made_tab_view = True
    created_tabs = {}  # Dictionary to store created tabs by their names

    def create_server_tab(tabview, server_info):
        server_name = server_info.get('displayName', "Server")
        
        # Check if tab with the same name already exists
        if server_name in created_tabs:
            tabview.select(created_tabs[server_name])  # Focus on existing tab
            return
        
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
                edit_properties_window(properties, properties_file)
            else:
                messagebox.showerror("Error", f"server.properties file not found at {properties_file}")

        def send_command():
            command = command_entry.get()
            print("command")
            if server_name in processes and processes[server_name].stdin:
                print("command is being run\n")
                processes[server_name].stdin.write(command + "\n")
                processes[server_name].stdin.flush()
            else:
                messagebox.showerror("Error", "Process is not running")

        def del_server_callback():
            del_server(server_info.get('displayName', "Unnamed Server"))
            if server_name in processes:
                del processes[server_name]
            if server_name in server_states:
                del server_states[server_name]
            tabview.delete(created_tabs[server_name])
            del created_tabs[server_name]

        def run_server_callback():
            if server_name not in processes or processes[server_name] is None:
                processes[server_name] = run_server(server_info, text_widget)
                if processes[server_name] is None:
                    messagebox.showerror("Error", "Failed to start the server")
                else:
                    print("Server process started")
        
        tab_name = server_info.get('displayName', "Server")
        server_tab = tabview.add(tab_name)
        created_tabs[server_name] = server_tab  # Add the created tab to the dictionary
       

        # tab_name = server_info.get('displayName', "Server")
        # server_tab = tabview.add(tab_name)

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

        if server_name in server_states:
            text_widget.insert(tk.END, server_states[server_name]['text'])
            if server_states[server_name]['is_running']:
                run_server_callback()

        command_entry = ctk.CTkEntry(server_tab)
        command_entry.pack(fill=tk.X, pady=5)

        send_button = ctk.CTkButton(server_tab, text="Send Command", command=send_command)
        send_button.pack(pady=5)


    for server in servers:
        if(server in made_servers):
            pass
        else:
            made_servers.append(server)
            create_server_tab(tabview, server)

