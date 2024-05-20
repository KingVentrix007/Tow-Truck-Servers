import tkinter as tk
from tkinter import filedialog, messagebox, Spinbox, ttk
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

main_icons_width = 40
main_icons_height = 40

# System Settings
customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

# Load Minecraft versions
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

# Create the main application window
app = customtkinter.CTk()
app.geometry("720x480")
app.title("Tow Truck Server")

# Load image using Pillow after the Tkinter root window is created
icon_image_pil = Image.open("mainicon.png")
icon_photo = ImageTk.PhotoImage(icon_image_pil)
app.iconbitmap("./icons8-tow-truck-64.ico")

# Global variable for the process
process = None

# Function to validate integer input
def validate_int_input(P):
    if P.isdigit() or P == "":
        return True
    return False

# Function to create a tooltip
class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        widget.bind("<Enter>", self.show_tooltip)
        widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        if self.tooltip_window or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify='left',
                         background="#ffffe0", relief='solid', borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide_tooltip(self, event=None):
        tw = self.tooltip_window
        self.tooltip_window = None
        if tw:
            tw.destroy()

# Function to load properties from a file
def load_properties(file_path):
    properties = {}
    with open(file_path, 'r') as file:
        for line in file:
            if '=' in line:
                key, value = line.strip().split('=', 1)
                properties[key] = value
    return properties

# Function to save properties to a file
def save_properties(file_path, properties):
    with open(file_path, 'w') as file:
        for key, value in properties.items():
            file.write(f"{key}={value}\n")

# Function to create a new tab for managing a specific server
def create_server_tab(notebook, server_info):
    global process
    
    def open_settings():
        path = server_info.get('path', "/fake/")
        properties_file = os.path.join(path, "server.properties")
        if os.path.exists(properties_file):
            properties = load_properties(properties_file)
            edit_properties_window(properties, properties_file)
        else:
            messagebox.showerror("Error", f"server.properties file not found at {properties_file}")

    def run_server():
        global process
        adjust_path()
        path = server_info.get('path', "/fake/")
        java = server_info.get('javaPath', "java")
        os.chdir(path)
        lib = makeserver.extract_libraries_path("run.bat")
        ram = server_info.get('ram', "2G")
        cmd = f"{java} -Xmx{ram} {lib} nogui %*"

        def run_command(command):
            global process
            process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                       text=True)
            for line in iter(process.stdout.readline, ""):
                console_output.insert(tk.END, line)
                console_output.see(tk.END)

        threading.Thread(target=run_command, args=(cmd,)).start()

    def stop_server():
        global process
        if process:
            process.stdin.write("stop\n")
            process.stdin.flush()
            process = None

    def adjust_path():
        path = server_info.get('path', "/fake/")
        makeserver.download_libs(path)
        makeserver.download_jar(path)

    def edit_properties_window(properties, properties_file):
        def save_properties_changes():
            properties.update({
                'server-port': server_port_entry.get(),
                'level-name': level_name_entry.get(),
                'motd': motd_entry.get(),
                'gamemode': gamemode_entry.get(),
                'enable-query': enable_query_var.get(),
                'enable-rcon': enable_rcon_var.get(),
                'rcon.password': rcon_password_entry.get(),
                'enable-command-block': enable_command_block_var.get(),
                'enable-command-block-output': enable_command_block_output_var.get(),
                'sync-chunk-writes': sync_chunk_writes_var.get(),
                'enable-jmx-monitoring': enable_jmx_monitoring_var.get(),
                'op-permission-level': op_permission_level_entry.get(),
                'prevent-proxy-connections': prevent_proxy_connections_var.get(),
                'resource-pack': resource_pack_entry.get(),
                'resource-pack-sha1': resource_pack_sha1_entry.get(),
                'difficulty': difficulty_entry.get(),
                'network-compression-threshold': network_compression_threshold_entry.get(),
                'max-tick-time': max_tick_time_entry.get(),
                'generator-settings': generator_settings_entry.get(),
                'force-gamemode': force_gamemode_var.get(),
                'broadcast-console-to-ops': broadcast_console_to_ops_var.get(),
                'spawn-npcs': spawn_npcs_var.get(),
                'spawn-animals': spawn_animals_var.get(),
                'spawn-monsters': spawn_monsters_var.get(),
                'snooper-enabled': snooper_enabled_var.get(),
                'hardcore': hardcore_var.get(),
                'online-mode': online_mode_var.get(),
                'pvp': pvp_var.get(),
                'difficulty': difficulty_var.get(),
                'spawn-protection': spawn_protection_var.get(),
                'max-players': max_players_var.get(),
                'server-ip': server_ip_var.get(),
                'allow-flight': allow_flight_var.get(),
                'spawn-protection': spawn_protection_var.get(),
                'white-list': white_list_var.get(),
                'generate-structures': generate_structures_var.get(),
                'level-seed': level_seed_var.get(),
                'enable-command-block': enable_command_block_var.get(),
                'server-name': server_name_var.get(),
                'enable-query': enable_query_var.get(),
                'query.port': query_port_var.get(),
                'enable-rcon': enable_rcon_var.get(),
                'rcon.port': rcon_port_var.get(),
                'rcon.password': rcon_password_var.get(),
                'broadcast-rcon-to-ops': broadcast_rcon_to_ops_var.get(),
                'broadcast-console-to-ops': broadcast_console_to_ops_var.get(),
                'sync-chunk-writes': sync_chunk_writes_var.get(),
                'enable-jmx-monitoring': enable_jmx_monitoring_var.get(),
                'max-tick-time': max_tick_time_var.get(),
                'view-distance': view_distance_var.get(),
                'server-port': server_port_var.get(),
                'resource-pack': resource_pack_var.get(),
                'resource-pack-sha1': resource_pack_sha1_var.get(),
                'hardcore': hardcore_var.get(),
                'pvp': pvp_var.get(),
                'spawn-npcs': spawn_npcs_var.get(),
                'spawn-animals': spawn_animals_var.get(),
                'spawn-monsters': spawn_monsters_var.get(),
                'generate-structures': generate_structures_var.get(),
                'max-build-height': max_build_height_var.get(),
                'online-mode': online_mode_var.get(),
                'level-type': level_type_var.get(),
                'allow-flight': allow_flight_var.get(),
                'gamemode': gamemode_var.get(),
                'player-idle-timeout': player_idle_timeout_var.get(),
                'max-players': max_players_var.get(),
                'network-compression-threshold': network_compression_threshold_var.get(),
                'resource-pack-sha1': resource_pack_sha1_var.get(),
                'max-world-size': max_world_size_var.get(),
                'resource-pack': resource_pack_var.get(),
                'server-ip': server_ip_var.get(),
                'spawn-protection': spawn_protection_var.get(),
                'allow-nether': allow_nether_var.get(),
                'rate-limit': rate_limit_var.get(),
                'enable-rcon': enable_rcon_var.get(),
                'motd': motd_var.get(),
            })

            save_properties(properties_file, properties)
            edit_properties_window.destroy()

        edit_properties_window = tk.Toplevel(app)
        edit_properties_window.title("Edit server.properties")
        edit_properties_window.geometry("500x500")
        edit_properties_window.resizable(False, False)

        properties_frame = ttk.LabelFrame(edit_properties_window, text="Server Properties")
        properties_frame.pack(fill="both", expand="yes", padx=20, pady=20)

        properties_labels = [
            "server-port", "level-name", "motd", "gamemode", "enable-query", "enable-rcon", "rcon.password",
            "enable-command-block", "enable-command-block-output", "sync-chunk-writes", "enable-jmx-monitoring",
            "op-permission-level", "prevent-proxy-connections", "resource-pack", "resource-pack-sha1", "difficulty",
            "network-compression-threshold", "max-tick-time", "generator-settings", "force-gamemode",
            "broadcast-console-to-ops", "spawn-npcs", "spawn-animals", "spawn-monsters", "snooper-enabled",
            "hardcore", "online-mode", "pvp", "difficulty", "spawn-protection", "max-players", "server-ip",
            "allow-flight", "spawn-protection", "white-list", "generate-structures", "level-seed",
            "enable-command-block", "server-name", "enable-query", "query.port", "enable-rcon", "rcon.port",
            "rcon.password", "broadcast-rcon-to-ops", "broadcast-console-to-ops", "sync-chunk-writes",
            "enable-jmx-monitoring", "max-tick-time", "view-distance", "server-port", "resource-pack",
            "resource-pack-sha1", "hardcore", "pvp", "spawn-npcs", "spawn-animals", "spawn-monsters",
            "generate-structures", "max-build-height", "online-mode", "level-type", "allow-flight", "gamemode",
            "player-idle-timeout", "max-players", "network-compression-threshold", "resource-pack-sha1",
            "max-world-size", "resource-pack", "server-ip", "spawn-protection", "allow-nether", "rate-limit",
            "enable-rcon", "motd",
        ]

        properties_entries = {}
        for index, label in enumerate(properties_labels):
            ttk.Label(properties_frame, text=label).grid(row=index, column=0, padx=10, pady=5)
            if label == 'motd':
                entry = ttk.Entry(properties_frame, width=30, textvariable=motd_var)
            else:
                entry = ttk.Entry(properties_frame, width=30)
            entry.insert(0, properties[label])
            entry.grid(row=index, column=1, padx=10, pady=5)
            properties_entries[label] = entry

        save_changes_button = ttk.Button(edit_properties_window, text="Save Changes", command=save_properties_changes)
        save_changes_button.pack(pady=10)
        edit_properties_window.mainloop()

    root = tk.Tk()
    root.title("Minecraft Server Maker")

    app = ttk.Frame(root, padding="3")
    app.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
    app.columnconfigure(0, weight=1)
    app.rowconfigure(0, weight=1)

    server_info = {}
    process = None
    motd_var = tk.StringVar()

    title_label = ttk.Label(app, text="Minecraft Server Maker")
    title_label.grid(column=0, row=0, columnspan=2)

    # -------------------------- Server Info --------------------------
    server_info_frame = ttk.LabelFrame(app, text="Server Info")
    server_info_frame.grid(column=0, row=1, sticky=(tk.W, tk.E), padx=10, pady=5)

    ttk.Label(server_info_frame, text="Server Path:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
    server_path_entry = ttk.Entry(server_info_frame, width=30)
    server_path_entry.grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)
    server_path_button = ttk.Button(server_info_frame, text="Browse")
    server_path_button.grid(row=0, column=2, sticky=tk.W, padx=10, pady=5)

    def on_server_path_button_click():
        path = filedialog.askdirectory()
        if path:
            server_path_entry.delete(0, tk.END)
            server_path_entry.insert(0, path)
            server_info['path'] = path
            adjust_path()

    server_path_button['command'] = on_server_path_button_click

    ttk.Label(server_info_frame, text="Server Version:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
    server_version_entry = ttk.Entry(server_info_frame, width=30)
    server_version_entry.grid(row=1, column=1, sticky=tk.W, padx=10, pady=5)

    # -------------------------- Server Properties --------------------------
    server_properties_frame = ttk.LabelFrame(app, text="Server Properties")
    server_properties_frame.grid(column=0, row=2, sticky=(tk.W, tk.E), padx=10, pady=5)

    ttk.Label(server_properties_frame, text="Server Port:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
    server_port_var = tk.StringVar()
    server_port_var.set("25565")
    server_port_entry = ttk.Entry(server_properties_frame, width=30, textvariable=server_port_var)
    server_port_entry.grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)

    ttk.Label(server_properties_frame, text="Level Name:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
    level_name_var = tk.StringVar()
    level_name_var.set("world")
    level_name_entry = ttk.Entry(server_properties_frame, width=30, textvariable=level_name_var)
    level_name_entry.grid(row=1, column=1, sticky=tk.W, padx=10, pady=5)

    ttk.Label(server_properties_frame, text="MOTD:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
    motd_entry = ttk.Entry(server_properties_frame, width=30, textvariable=motd_var)
    motd_entry.grid(row=2, column=1, sticky=tk.W, padx=10, pady=5)

    ttk.Label(server_properties_frame, text="Gamemode:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
    gamemode_var = tk.StringVar()
    gamemode_var.set("survival")
    gamemode_entry = ttk.Entry(server_properties_frame, width=30, textvariable=gamemode_var)
    gamemode_entry.grid(row=3, column=1, sticky=tk.W, padx=10, pady=5)

    ttk.Label(server_properties_frame, text="Enable Query:").grid(row=4, column=0, sticky=tk.W, padx=10, pady=5)
    enable_query_var = tk.BooleanVar()
    enable_query_var.set(True)
    enable_query_check = ttk.Checkbutton(server_properties_frame, variable=enable_query_var)
    enable_query_check.grid(row=4, column=1, sticky=tk.W, padx=10, pady=5)

    ttk.Label(server_properties_frame, text="Enable RCON:").grid(row=5, column=0, sticky=tk.W, padx=10, pady=5)
    enable_rcon_var = tk.BooleanVar()
    enable_rcon_var.set(False)
    enable_rcon_check = ttk.Checkbutton(server_properties_frame, variable=enable_rcon_var)
    enable_rcon_check.grid(row=5, column=1, sticky=tk.W, padx=10, pady=5)

    ttk.Label(server_properties_frame, text="RCON Password:").grid(row=6, column=0, sticky=tk.W, padx=10, pady=5)
    rcon_password_var = tk.StringVar()
    rcon_password_entry = ttk.Entry(server_properties_frame, width=30, textvariable=rcon_password_var)
    rcon_password_entry.grid(row=6, column=1, sticky=tk.W, padx=10, pady=5)

    ttk.Label(server_properties_frame, text="Enable Command Block:").grid(row=7, column=0, sticky=tk.W, padx=10, pady=5)
    enable_command_block_var = tk.BooleanVar()
    enable_command_block_var.set(False)
    enable_command_block_check = ttk.Checkbutton(server_properties_frame, variable=enable_command_block_var)
    enable_command_block_check.grid(row=7, column=1, sticky=tk.W, padx=10, pady=5)

    ttk.Label(server_properties_frame, text="Enable Command Block Output:").grid(row=8, column=0, sticky=tk.W, padx=10, pady=5)
    enable_command_block_output_var = tk.BooleanVar()
    enable_command_block_output_var.set(True)
    enable_command_block_output_check = ttk.Checkbutton(server_properties_frame, variable=enable_command_block_output_var)
    enable_command_block_output_check.grid(row=8, column=1, sticky=tk.W, padx=10, pady=5)

    ttk.Label(server_properties_frame, text="Sync Chunk Writes:").grid(row=9, column=0, sticky=tk.W, padx=10, pady=5)
    sync_chunk_writes_var = tk.BooleanVar()
    sync_chunk_writes_var.set(False)
    sync_chunk_writes_check = ttk.Checkbutton(server_properties_frame, variable=sync_chunk_writes_var)
    sync_chunk_writes_check.grid(row=9, column=1, sticky=tk.W, padx=10, pady=5)

    ttk.Label(server_properties_frame, text="Enable JMX Monitoring:").grid(row=10, column=0, sticky=tk.W, padx=10, pady=5)
    enable_jmx_monitoring_var = tk.BooleanVar()
    enable_jmx_monitoring_var.set(False)
    enable_jmx_monitoring_check = ttk.Checkbutton(server_properties_frame, variable=enable_jmx_monitoring_var)
    enable_jmx_monitoring_check.grid(row=10, column=1, sticky=tk.W, padx=10, pady=5)

    ttk.Label(server_properties_frame, text="OP Permission Level:").grid(row=11, column=0, sticky=tk.W, padx=10, pady=5)
    op_permission_level_var = tk.StringVar()
    op_permission_level_var.set("4")
    op_permission_level_entry = ttk.Entry(server_properties_frame, width=30, textvariable=op_permission_level_var)
    op_permission_level_entry.grid(row=11, column=1, sticky=tk.W, padx=10, pady=5)

    ttk.Label(server_properties_frame, text="Prevent Proxy Connections:").grid(row=12, column=0, sticky=tk.W, padx=10, pady=5)
    prevent_proxy_connections_var = tk.BooleanVar()
    prevent_proxy_connections_var.set(False)
    prevent_proxy_connections_check = ttk.Checkbutton(server_properties_frame, variable=prevent_proxy_connections_var)
    prevent_proxy_connections_check.grid(row=12, column=1, sticky=tk.W, padx=10, pady=5)

    ttk.Label(server_properties_frame, text="Resource Pack:").grid(row=13, column=0, sticky=tk.W, padx=10, pady=5)
    resource_pack_var = tk.StringVar()
    resource_pack_entry = ttk.Entry(server_properties_frame, width=30, textvariable=resource_pack_var)
    resource_pack_entry.grid(row=13, column=1, sticky=tk.W, padx=10, pady=5)

    ttk.Label(server_properties_frame, text="Resource Pack SHA1:").grid(row=14, column=0, sticky=tk.W, padx=10, pady=5)
    resource_pack_sha1_var = tk.StringVar()
    resource_pack_sha1_entry = ttk.Entry(server_properties_frame, width=30, textvariable=resource_pack_sha1_var)
    resource_pack_sha1_entry.grid(row=14, column=1, sticky=tk.W, padx=10, pady=5)

    # -------------------------- Server Control Buttons --------------------------
    server_control_frame = ttk.LabelFrame(app, text="Server Control")
    server_control_frame.grid(column=0, row=3, sticky=(tk.W, tk.E), padx=10, pady=5)

    run_button = ttk.Button(server_control_frame, text="Run", command=run_server)
    run_button.grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)

    stop_button = ttk.Button(server_control_frame, text="Stop", command=stop_server)
    stop_button.grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)

    settings_button = ttk.Button(server_control_frame, text="Settings", command=open_settings)
    settings_button.grid(row=0, column=2, sticky=tk.W, padx=10, pady=5)

    # -------------------------- Console Output --------------------------
    console_frame = ttk.LabelFrame(app, text="Console Output")
    console_frame.grid(column=0, row=4, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=5)

    console_output = ScrolledText(console_frame, wrap=tk.WORD, width=80, height=10)
    console_output.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=5)
    console_output.insert(tk.END, "Welcome to Minecraft Server Maker!\n")

    console_scrollbar = ttk.Scrollbar(console_frame, orient="vertical", command=console_output.yview)
    console_scrollbar.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
    console_output["yscrollcommand"] = console_scrollbar.set

    root.mainloop()

# -------------------------- Main UI --------------------------
notebook = ttk.Notebook(app)
notebook.pack(fill="both", expand=True)

for i in range(3):  # Change the range to however many servers you want to create tabs for
    server_info = {
        "path": f"server{i+1}",
        "javaPath": "java",
        "ram": "2G"
    }
    tab_frame = ttk.Frame(notebook)
    notebook.add(tab_frame, text=f"Server {i+1}")
    create_server_tab(tab_frame, server_info)

app.mainloop()
