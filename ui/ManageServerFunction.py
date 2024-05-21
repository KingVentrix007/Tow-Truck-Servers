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

def ManageServerFunction(window, parent_screen_function):
    clear_window(window)

    servers = get_all_servers()
    
    tabview = ctk.CTkTabview(window)
    tabview.pack(expand=1, fill='both')

    def create_server_tab(tabview, server_info):
        server_name = server_info.get('displayName', "Server")

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
            tabview.delete(tab_name)

        def run_server_callback():
            if server_name not in processes or processes[server_name] is None:
                processes[server_name] = run_server(server_info, text_widget)
                if processes[server_name] is None:
                    messagebox.showerror("Error", "Failed to start the server")
                else:
                    print("Server process started")

        tab_name = server_info.get('displayName', "Server")
        if tab_name in tabview._tab_dict:
            tabview.delete(tab_name)
        server_tab = tabview.add(tab_name)

        def back_tab():
            server_states[server_name] = {
                'text': text_widget.get('1.0', tk.END),
                'is_running': processes.get(server_name) is not None,
            }
            print(tabview._tab_dict.keys())
            current_tabs = tabview._tab_dict.keys()
            tab_name_t = current_Server_data.get('displayName', "Server")
            if tab_name_t in current_tabs:
                tabview.delete(tab_name_t)
            adjust_path()
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

        if server_name in server_states:
            text_widget.insert(tk.END, server_states[server_name]['text'])
            if server_states[server_name]['is_running']:
                run_server_callback()

        command_entry = ctk.CTkEntry(server_tab)
        command_entry.pack(fill=tk.X, pady=5)

        send_button = ctk.CTkButton(server_tab, text="Send Command", command=send_command)
        send_button.pack(pady=5)

    for server in servers:
        create_server_tab(tabview, server)

    def simple_back():
        for server_name, server_state in server_states.items():
            text_widget_content = server_state['text']
            if server_name in processes and processes[server_name] is not None:
                server_state['text'] = text_widget.get('1.0', tk.END)
                server_state['is_running'] = processes.get(server_name) is not None
        adjust_path()
        parent_screen_function()

    back_button = ctk.CTkButton(window, text="Back", command=simple_back)
    back_button.pack(pady=10)

