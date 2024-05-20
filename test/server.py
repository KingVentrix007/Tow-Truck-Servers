import os
import tkinter as tk
import customtkinter as ctk
from threading import Thread
from mods.modloader import download_server_jar




def install_server(name,version,modloader):
    pass

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

    
    download_thread = Thread(target=download_server_jar, args=(name, version, progress_var, on_complete,modloader))
    download_thread.start()
    
    jar_download_window.mainloop()