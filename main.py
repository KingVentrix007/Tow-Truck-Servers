import tkinter as tk
from tkinter import filedialog, messagebox, Spinbox
from tkinter.scrolledtext import ScrolledText
import subprocess
import customtkinter
import customtkinter as ctk
from PIL import Image, ImageTk
import random
import string
import makeserver as makeserver
import json
import os
import shutil
import threading
from CTkSpinbox import *
# from 
from tkinter import messagebox
from tkinter import ttk
# System Settings
customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("green")
def animate_tow_truck(canvas, image, x, y, dx):
    canvas.move(image, dx, 0)
    if canvas.coords(image)[0] > 100:
        canvas.after(50, animate_tow_truck, canvas, image, x, y, dx)
minecraft_versions = [
    # List of Minecraft versions
    "1.20.6", "1.20.5", "1.20.4", "1.20.3", "1.20.2", "1.20.1", "1.20",
    "1.19.4", "1.19.3", "1.19.2", "1.19.1", "1.19", "1.18.2", "1.18.1", "1.18",
    "1.17.1", "1.17", "1.16.5", "1.16.4", "1.16.3", "1.16.2", "1.16.1", "1.16",
    "1.15.2", "1.15.1", "1.15", "1.14.4", "1.14.3", "1.14.2", "1.14.1", "1.14",
    "1.13.2", "1.13.1", "1.13", "1.12.2", "1.12.1", "1.12", "1.11.2", "1.11.1",
    "1.11", "1.10.2", "1.10.1", "1.10", "1.9.4", "1.9.3", "1.9.2", "1.9.1",
    "1.9", "1.8.9", "1.8.8", "1.8.7", "1.8.6", "1.8.5", "1.8.4", "1.8.3", "1.8.2",
    "1.8.1", "1.8", "1.7.10", "1.7.9", "1.7.8", "1.7.7", "1.7.6", "1.7.5", "1.7.4",
    "1.7.2", "1.6.4", "1.6.2", "1.6.1", "1.5.2", "1.5.1", "1.5", "1.4.7", "1.4.6",
    "1.4.5", "1.4.4", "1.4.2", "1.3.2", "1.3.1", "1.2.5", "1.2.4", "1.2.3", "1.2.2",
    "1.2.1", "1.1", "1.0.1", "1.0.0"
]

# App
app = customtkinter.CTk()
app.geometry("720x480")
app.title("Tow Truck Server")

# Load image using Pillow after the Tkinter root window is created
icon_image_pil = Image.open("mainicon.png")
icon_photo = ImageTk.PhotoImage(icon_image_pil)  # Create a PhotoImage object for the window icon
app.iconbitmap("./icons8-tow-truck-64.ico")
# Create canvas

# Global variable for the process
process = None

# Functions
def clear_window():
    for widget in app.winfo_children():
        widget.destroy()
def load_properties(file_path):
    properties = {}
    with open(file_path, 'r') as file:
        for line in file:
            if '=' in line:
                key, value = line.strip().split('=', 1)
                properties[key] = value
    return properties

def save_properties(file_path, properties):
    with open(file_path, 'w') as file:
        for key, value in properties.items():
            file.write(f"{key}={value}\n")
def validate_int_input(P):
    if P.isdigit() or P == "":
        return True
    return False

def mod_menu(path,back_window=None):
    clear_window()
    # print("HERE",path)
    # window = ctk.CTk()
    # window.title("Mod Menu")
    # window.geometry("800x600")

    canvas = ctk.CTkCanvas(app)
    canvas.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)

    scrollbar = ctk.CTkScrollbar(app, command=canvas.yview)
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
    def back():
        clear_window()
        if(back_window==None):
            ManageServerFunction()
    # Position the frame on the left side of the window
    frame.pack(side=ctk.LEFT, fill=ctk.Y)
    BackBtn = customtkinter.CTkButton(app,text="Back",command=back)
    BackBtn.pack(side=ctk.BOTTOM)
    
    # window.mainloop()
# Example usage:
# mod_menu("F:/ServerWrapper/servers/Test")
# 


def edit_properties_window(properties, file_path):
    def save_changes():
        for key, widget in widgets.items():
            if isinstance(widget, tk.BooleanVar):
                properties[key] = 'true' if widget.get() else 'false'
            else:
                properties[key] = widget.get()
        save_properties(file_path, properties)
        # window.destroy()
        clear_window()
        ManageServerFunction()
        messagebox.showinfo("Save", "Properties saved successfully")

    def on_mousewheel(event):
        canvas.yview_scroll(-1 * int(event.delta / 120), "units")

    window = ctk.CTk()
    window.title("Edit Server Properties")
    window.geometry("800x600")

    ctk.set_appearance_mode("dark")  # Choose dark theme
    window.configure(bg="#2b2b2b")
    main_frame = ctk.CTkFrame(window)
    main_frame.pack(fill=tk.BOTH, expand=True)
    # main_frame.config(bg="#2b2b2b")
    canvas = ctk.CTkCanvas(main_frame,bg="#2b2b2b")
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = ctk.CTkScrollbar(main_frame, orientation=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    canvas.configure(yscrollcommand=scrollbar.set,borderwidth=0,highlightthickness=0)
    canvas.bind_all("<MouseWheel>", on_mousewheel)

    sub_frame = ctk.CTkFrame(canvas)
    # sub_frame.configure(borderwidth=0)
    canvas.create_window((0, 0), window=sub_frame, anchor="nw")

    widgets = {}
    row = 0

    vcmd = (window.register(validate_int_input), '%P')

    for key, value in properties.items():
        label = ctk.CTkLabel(sub_frame, text=key)
        label.grid(row=row, column=0, sticky='w', padx=5, pady=5)

        if value.lower() in ('true', 'false'):
            var = tk.BooleanVar(value=value.lower() == 'true')
            checkbox = ctk.CTkCheckBox(sub_frame, variable=var,text="")
            checkbox.grid(row=row, column=1, sticky='w', padx=5, pady=5)
            widgets[key] = var
        elif value.isdigit():
            entry = ctk.CTkEntry(sub_frame, validate='key', validatecommand=vcmd)
            entry.insert(0, value)
            entry.grid(row=row, column=1, sticky='w', padx=5, pady=5)
            widgets[key] = entry
        else:
            entry = ctk.CTkEntry(sub_frame)
            entry.insert(0, value)
            entry.grid(row=row, column=1, sticky='w', padx=5, pady=5)
            widgets[key] = entry

        row += 1

    sub_frame.update_idletasks()  # Ensure sub_frame is updated with widgets
    canvas.config(scrollregion=canvas.bbox("all"))  # Update scroll region

    save_button = ctk.CTkButton(window, text="Save", command=save_changes)
    save_button.pack(side=tk.RIGHT, padx=5, pady=5, fill=tk.X)

    window.mainloop()

def adjust_path():
    current_path = os.getcwd()
    print(f"Current path: {current_path}")

    if 'servers' in current_path:
        path_parts = current_path.split(os.sep)
        new_path_parts = []
        for part in path_parts:
            if part == 'servers':
                break
            new_path_parts.append(part)
        new_path = os.sep.join(new_path_parts)
        
        if new_path:
            os.chdir(new_path)
            print(f"Adjusted path: {new_path}")
        else:
            print("New path is empty. Path adjustment failed.")
    else:
        print("The current path does not contain 'servers'.")

def del_server(name: str):
    data = makeserver.get_server(name)
    path = data["path"]
    remove_server_by_display_name(name)
    shutil.rmtree(path)

def remove_server_by_display_name(display_name: str, config_path='config.json'):
    try:
        with open(config_path, 'r') as file:
            config = json.load(file)
    except FileNotFoundError:
        print("Config file not found.")
        return False
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return False

    servers = config.get('servers', [])

    updated_servers = [server for server in servers if server.get('displayName') != display_name]
    
    config['servers'] = updated_servers

    try:
        with open(config_path, 'w') as file:
            json.dump(config, file, indent=4)
        print(f"Server with display name '{display_name}' removed successfully.")
        return True
    except Exception as e:
        print(f"Error writing to config file: {e}")
        return False

def get_all_servers(config_path='config.json'):
    try:
        with open(config_path, 'r') as file:
            config = json.load(file)
    except FileNotFoundError:
        print("Config file not found.")
        return []
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return []

    return config.get('servers', [])

def generate_random_seed():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

def update_seed_label(seed_label):
    new_seed = generate_random_seed()
    seed_label.configure(text=new_seed)

def AddServerScreen():
    clear_window()
    
    # Server Name input
    server_name_label = customtkinter.CTkLabel(app, text="Server Name:")
    server_name_label.place(relx=0.3, rely=0.2, anchor=customtkinter.E)
    server_name_entry = customtkinter.CTkEntry(app)
    server_name_entry.place(relx=0.5, rely=0.2, anchor=customtkinter.W)

    # Server Description input
    server_description_label = customtkinter.CTkLabel(app, text="Server Description:")
    server_description_label.place(relx=0.3, rely=0.3, anchor=customtkinter.E)
    server_description_entry = customtkinter.CTkEntry(app)
    server_description_entry.place(relx=0.5, rely=0.3, anchor=customtkinter.W)

    # Game Version dropdown
    game_version_label = customtkinter.CTkLabel(app, text="Game Version:")
    game_version_label.place(relx=0.3, rely=0.4, anchor=customtkinter.E)
    game_version_combobox = customtkinter.CTkComboBox(app, values=minecraft_versions)
    game_version_combobox.set(minecraft_versions[0])
    game_version_combobox.place(relx=0.5, rely=0.4, anchor=customtkinter.W)
    
    # Seed label and button
    seed_label = customtkinter.CTkLabel(app, text=generate_random_seed())
    seed_label.place(relx=0.5, rely=0.5, anchor=customtkinter.W)
    random_seed_button = customtkinter.CTkButton(app, text="Random Seed", command=lambda: update_seed_label(seed_label))
    random_seed_button.place(relx=0.8, rely=0.5, anchor=customtkinter.CENTER)

    # Add Server button
    def add_server():
        name = server_name_entry.get()
        description = server_description_entry.get()
        version = game_version_combobox.get()  # Get the selected version from the combobox
        seed = seed_label.cget("text")  # Get the current text of the seed label
        makeserver.make_server(name, description, version, seed)  # Call the make_server function with the provided parameters
    
    add_server_button = customtkinter.CTkButton(app, text="Add Server", command=add_server)
    add_server_button.place(relx=0.5, rely=0.6, anchor=customtkinter.CENTER)

    # Back button
    back_button = customtkinter.CTkButton(app, text="Back", command=main_screen)
    back_button.place(relx=0.5, rely=0.7, anchor=customtkinter.CENTER)

def ManageServerFunction():
    clear_window()

    servers = get_all_servers()

    def create_server_window(server_info):
        global process  # Ensure process is global

        def open_settings():
            path = server_info.get('path', "/fake/")
            properties_file = os.path.join(path, "server.properties")
            print("properties_file ==",properties_file)
            if os.path.exists(properties_file):
                properties = load_properties(properties_file)
                edit_properties_window(properties, properties_file)
            else:
                messagebox.showerror("Error", f"server.properties file not found at {properties_file}")

        def run_server():
            global process  # Ensure process is global
            adjust_path()

            path = server_info.get('path', "/fake/")
            java = server_info.get('javaPath', "java")
            os.chdir(path)
            print("PATH == ", os.getcwd())
            lib = makeserver.extract_libraries_path("run.bat")
            ram = server_info.get('ram', "2G")
            cmd = f"{java} -Xmx{ram} {lib} nogui %*"

            def run_command(command):
                global process  # Ensure process is global
                print(command)
                process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
                for line in iter(process.stdout.readline, ""):
                    print(line)
                    formatted_output = format_output_as_html(line)
                    text_widget.insert(tk.END, formatted_output)
                    text_widget.see(tk.END)  # Auto-scroll to the end
                process.stdout.close()
                process.wait()

            def format_output_as_html(output):
                output = output.replace('ERROR', '[ERROR]')
                output = output.replace('WARNING', '[WARNING]')
                output = output.replace('INFO', '[INFO]')
                return f'{output}'

            thread = threading.Thread(target=run_command, args=(cmd,), daemon=True)
            thread.start()
            print(thread.is_alive())

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
        def back():
            clear_window()
            ManageServerFunction()
        clear_window()
        # server_window = ctk.CTk()
        # server_window.geometry("800x600")
        # server_window.title(server_info.get('displayName', "Server"))

        # Create a frame for the top menu bar
        menu_bar = ctk.CTkFrame(app)
        menu_bar.pack(side=tk.TOP, fill=tk.X)

        delete_button = ctk.CTkButton(menu_bar, text="Delete", command=del_server_callback)
        delete_button.pack(side=tk.LEFT, padx=5, pady=5)
        back_button = ctk.CTkButton(menu_bar,text="Back", command=back)
        run_button = ctk.CTkButton(menu_bar, text="Run", command=run_server)
        run_button.pack(side=tk.LEFT, padx=5, pady=5)

        settings_button = ctk.CTkButton(menu_bar, text="Settings", command=open_settings)
        settings_button.pack(side=tk.LEFT, padx=5, pady=5)

        mod_btn = ctk.CTkButton(menu_bar, text="Mod Menu",command=lambda: mod_menu(server_info.get('path','null')))
        mod_btn.pack(side=tk.LEFT, padx=5, pady=5)
        back_button.pack(side=tk.LEFT,padx=5, pady=5)
        text_widget = ScrolledText(app, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True)

        command_entry = ctk.CTkEntry(app)
        command_entry.pack(fill=tk.X, pady=5)

        send_button = ctk.CTkButton(app, text="Send Command", command=send_command)
        send_button.pack(pady=5)

        # server_window.mainloop()
    for idx, server in enumerate(servers):
        display_name = server.get('displayName', f"Server {idx+1}")
        server_button = customtkinter.CTkButton(app, text=display_name, command=lambda server_info=server: create_server_window(server_info))
        server_button.grid(row=idx, column=0, padx=10, pady=5)

    back_button = customtkinter.CTkButton(app, text="Back", command=main_screen)
    back_button.grid(row=len(servers), column=0, pady=10)

def main_screen():
    clear_window()
    AddServer = customtkinter.CTkButton(app, text="Add Server", command=AddServerScreen)
    AddServer.place(relx=0.5, rely=0.5, anchor=customtkinter.CENTER)

    ManageServer = customtkinter.CTkButton(app, text="Manage Server", command=ManageServerFunction)
    ManageServer.place(relx=0.5, rely=0.56, anchor=customtkinter.CENTER)

    Credits = customtkinter.CTkButton(app, text="Credits")
    Credits.place(relx=1.0, rely=1.0, anchor=customtkinter.SE)


# Create canvas
# canvas = tk.Canvas(app, width=720, height=480, bg="#2b2b2b", highlightthickness=0)
# canvas.pack()

# Add tow truck image to canvas
# tow_truck = canvas.create_image(600, 200, image=icon_photo, anchor=tk.NW)  # Set initial position and anchor

# Animation
# animate_tow_truck(canvas, tow_truck, 600, 200, -5)  # Negative value for leftward movement

# Add text after tow truck animation
# canvas.create_text(360, 240, text="Tow Truck Servers", font=("Helvetica", 24), fill="white")  # Adjust text fill color

# After animation, create main screen
# app.after(6000, main_screen)  # Call create_main_screen after 5 seconds
main_screen()
app.mainloop()
