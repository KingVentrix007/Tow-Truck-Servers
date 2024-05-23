import os
import tkinter as tk
import customtkinter as ctk
from threading import Thread
from mods.modloader import download_server_jar
from mods.fabric import install_fabric_server
from mods.forge import install_forge_server
from file_utils.path_management import adjust_path
from server_utils.server_manager import add_entry
def install_server(name,jar_file,modloader):
    if(modloader == "fabric"):
        install_fabric_server(name,jar_file)
    elif(modloader == "forge"):
        install_forge_server(name=name,jar_file=jar_file)
    else:
        return -1
def make_server(name, description, version, seed,img,modloader):
    valid_server_name = name.replace(" ","")
    if(os.path.exists(valid_server_name)):
        return -1
    os.makedirs(f"./servers/{valid_server_name}", exist_ok=True)
    jar_download_window = ctk.CTk()
    jar_download_window.title("Downloading Server Jar")
    jar_download_window.geometry("30x40")
    progress_var = tk.DoubleVar(jar_download_window, 0.0)
    progressbar = ctk.CTkProgressbar(jar_download_window, variable=progress_var, maximum=100)
    progressbar.pack(pady=10)
    def on_complete(name, version):
        jar_download_window.destroy()
        install_server(name, version, modloader)
        adjust_path()
        add_entry(name=name, game_version=version,description=description,modloader=modloader,img=img)
        

    
    download_thread = Thread(target=download_server_jar, args=(name, version, progress_var, on_complete,modloader))
    download_thread.start()
    
    jar_download_window.mainloop()