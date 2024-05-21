import tkinter as tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
import customtkinter as ctk
from ui.general import clear_window
from server_utils.server_manager import get_all_servers,load_properties,del_server
from ui.settings import edit_properties_window
from ui.ModMenu import mod_menu
from server_utils.server import run_server
from file_utils.path_mangment import adjust_path
import os

current_Server_data = ""

def ManageServerFunction(window,parent_screen_function):
    clear_window(window)

    servers = get_all_servers()
    
    def create_server_window(server_info):
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
                edit_properties_window(properties, properties_file,server_window,back_window)
            else:
                messagebox.showerror("Error", f"server.properties file not found at {properties_file}")


            

        def send_command():
            global process  # Ensure process is global
            command = command_entry.get()
            print("command")
            print("Process == ", process)
            print("process.stdin == ", process.stdin)
            if process and process.stdin:
                print("command is being run\n")
                process.stdin.write(command + "\n")
                process.stdin.flush()

        def del_server_callback():
            # server_window.destroy()
            del_server(server_info.get('displayName', "Unnamed Server"))
        # clear_window()
        server_window = ctk.CTk()
        server_window.geometry("800x600")
        server_window.title(server_info.get('displayName', "Server"))
        def back_window():
            create_server_window(current_Server_data)
        # Create a frame for the top menu bar
        menu_bar = ctk.CTkFrame(server_window)
        menu_bar.pack(side=tk.TOP, fill=tk.X)

        delete_button = ctk.CTkButton(menu_bar, text="Delete", command=del_server_callback)
        delete_button.pack(side=tk.LEFT, padx=5, pady=5)
        run_button = ctk.CTkButton(menu_bar, text="Run", command=lambda: run_server(server_info,text_widget))
        run_button.pack(side=tk.LEFT, padx=5, pady=5)

        settings_button = ctk.CTkButton(menu_bar, text="Settings", command=open_settings)
        settings_button.pack(side=tk.LEFT, padx=5, pady=5)

        mod_btn = ctk.CTkButton(menu_bar, text="Mod Menu",command=lambda: mod_menu(server_info.get('path','null')))
        mod_btn.pack(side=tk.LEFT, padx=5, pady=5)
        # back_button.pack(side=tk.LEFT,padx=5, pady=5)
        text_widget = ScrolledText(server_window, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True)

        command_entry = ctk.CTkEntry(server_window)
        command_entry.pack(fill=tk.X, pady=5)

        send_button = ctk.CTkButton(server_window, text="Send Command", command=send_command)
        send_button.pack(pady=5)

        server_window.mainloop()
    for idx, server in enumerate(servers):
        display_name = server.get('displayName', f"Server {idx+1}")
        server_button = ctk.CTkButton(window, text=display_name, command=lambda server_info=server: create_server_window(server_info))
        server_button.grid(row=idx, column=0, padx=10, pady=5)

    back_button = ctk.CTkButton(window, text="Back", command=parent_screen_function)
    back_button.grid(row=len(servers), column=0, pady=10)
