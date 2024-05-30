import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
import os
from threading import Thread
import requests
from io import BytesIO
from PIL import Image, ImageTk
import mods.apiv2 as apiv2
from config.debug import setup_logging,log
import json
from tkinter import messagebox
def download_file(url, local_filename, progress, root, label, callback=None):
    with requests.get(url, stream=True) as response:
        response.raise_for_status()
        total_length = int(response.headers.get('content-length', 0))
        downloaded = 0

        with open(local_filename, 'wb') as out_file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    out_file.write(chunk)
                    downloaded += len(chunk)
                    progress["value"] = (downloaded / total_length) * 100
                    root.update_idletasks()

    if callback:
        callback()
def ensure_config_exists(config_path):
    if not os.path.exists(config_path):
        with open(config_path, 'w') as config_file:
            json.dump({"mods": []}, config_file)

def load_config(config_path):
    with open(config_path, 'r') as config_file:
        return json.load(config_file)

def save_config(config_path, config):
    with open(config_path, 'w') as config_file:
        json.dump(config, config_file, indent=4)

def show_waiting_window(mod_title):
    waiting_root = tk.Toplevel()
    waiting_root.title("Please Wait")
    waiting_label = ttk.Label(waiting_root, text=f"Searching for mod URLs for {mod_title}...\nThis may take a while, please be patient")
    waiting_label.pack(pady=20, padx=20)
    return waiting_root

def close_waiting_window(waiting_root):
    if waiting_root:
        waiting_root.destroy()

def fetch_mod_urls(mod_data, server_info):
    mod_urls = apiv2.get_download_urls(mod_data["project_id"], server_info.get("gameVersion", "0.0"), server_info.get("modloader", "null"))
    log(mod_urls)
    if(len(mod_urls) >=1):
        return mod_urls[0]
    return None 
def download_mod(mod_data, server_info):
    server_folder = server_info.get("path")
    config_path = os.path.join(server_folder, 'towtruckconfig.json')
    mod_id = mod_data["project_id"]
    log("MOD_DATA=", mod_data)
    
    ensure_config_exists(config_path)
    config = load_config(config_path)   
    if mod_id not in [mod_id for mod in config["mods"] for mod_id in mod.keys()]:
        pass
    else:
        log(f"Mod {mod_id} is already installed, skipping download.")
        return

    waiting_window = show_waiting_window(mod_data.get("title"))

    def download_mod_files():
        nonlocal config

        urls = fetch_mod_urls(mod_data, server_info)
        if(urls == None):
            messagebox.showerror("Failed to get mod urls","Failed to get mod_urls, please report this error, with the mod name, server version and mod loader")
        else:
            url = urls["url"]
            mod_file_name = os.path.basename(url)
            config["mods"].append({mod_id: mod_file_name})
            save_config(config_path, config)

            dependencies = urls["dependencies"]
            close_waiting_window(waiting_window)
            mod_folder = os.path.normpath(os.path.join(server_info.get("path", ""), "mods"))
            os.makedirs(mod_folder, exist_ok=True)

            root = tk.Tk()
            root.title("Download Progress")
            mod_name = mod_data["title"]
            label = ttk.Label(root, text=f"Downloading mod {mod_name}...")
            label.pack(pady=10)
            progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
            progress.pack(pady=10)

            def start_download():
                local_filename = os.path.join(mod_folder, mod_file_name)
                download_file(url, local_filename, progress, root, label, callback=lambda: download_dependencies(dependencies, config, config_path, mod_folder, progress, root, label))
                config["mods"].append({mod_id: mod_file_name})
                log("config45 = ",config)
                save_config(config_path, config)
                log(f"Downloaded mod to {local_filename}")

            Thread(target=start_download).start()
            root.mainloop()
            

    Thread(target=download_mod_files).start()
def download_dependencies(dependencies, config, config_path, mod_folder, progress, root, label):
    label.config(text="Mod download complete! Downloading dependencies...")
    for dep in dependencies:
        dep_id = dep["id"]
        dep_url = dep["url"]
        #EEE
        log(f"dependencies {dep_id} url: {dep_url}" )
        if dep_id not in [mod_id for mod in config["mods"] for mod_id in mod.keys()] and dep_url:
            dep_file_name = os.path.basename(dep_url)
            local_dep_filename = os.path.join(mod_folder, dep_file_name)
            download_file(dep_url, local_dep_filename, progress, root, label)
            config["mods"].append({dep_id: dep_file_name})
            save_config(config_path, config)
        else:
            log(f"Dependency {dep_id} already exists, skipping download.")
    label.config(text="All downloads complete!")
    log("Downloaded all dependencies.")
    root.destroy()
def get_mod_data(query=None,loaders="forge",version="1.19.2"):
    print("Searching,,,")
    # Simulate retrieving data based on the query
    mod_data_info,ids = apiv2.search_mods_internal(query=query,modloader=loaders,version=version)
    mod_data = []
    for mod in mod_data_info:
        mod_name = mod["title"]
        mod_author = mod["author"]
        icon_url = mod["icon_url"]
        entry = {
            "mod_name":mod_name,
            "author":mod_author,
            "icon_url":icon_url
        }
        mod_data.append(entry)
    print(len(mod_data))
    # import time
    # time.sleep(4)  # Simulating a delay
    mod_data_temp = [
        {"mod_name": "Sample Mod 1", "author": "Author 1", "url": "https://via.placeholder.com/150"},
        {"mod_name": "Sample Mod 2", "author": "Author 2", "url": "https://via.placeholder.com/150"},
        {"mod_name": "Sample Mod 3", "author": "Author 3", "url": "https://via.placeholder.com/150"},
    ]
    # if query:
        # mod_data = [mod for mod in mod_data if query.lower() in mod["mod_name"].lower()]
    return mod_data_info

def download_mod(server_data,mod_data):
    mod_name = mod_data["title"]
    print(f"Downloading mod: {mod_name}")

class ModFetcherApp(ctk.CTk):
    def __init__(self,loader,version,server_info):
        super().__init__()
        self.title("Mod Fetcher")
        self.geometry("400x400")
        self.mod_loader = loader
        self.game_version = version
        self.server_data = server_info
        self.search_var = tk.StringVar()
        
        self.search_entry = ctk.CTkEntry(self, textvariable=self.search_var)
        self.search_entry.pack(pady=10)
        
        self.search_button = ctk.CTkButton(self, text="Search", command=self.on_search_clicked)
        self.search_button.pack()
        
        self.canvas = ctk.CTkCanvas(self)
        self.frame = ctk.CTkFrame(self.canvas)
        self.scrollbar = ctk.CTkScrollbar(self, orientation="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set,bg="#2b2b2b")
        
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")
        
        self.frame.bind("<Configure>", self.on_frame_configure)
        
        # Dictionary to store image data
        self.image_data = {}
        
    def on_search_clicked(self):
        query = self.search_var.get()
        self.update_mod_data(query)
        
    def update_mod_data(self, query):
        thread = Thread(target=self.fetch_mod_data, args=(query,))
        thread.start()
        
    def fetch_mod_data(self, query=None):
        mod_data = get_mod_data(query,self.mod_loader,self.game_version)
        self.update_ui(mod_data)
        
    def fetch_image_data(self, mod_data):
        for mod in mod_data:
            url = mod['icon_url']
            response = requests.get(url)
            image_data = BytesIO(response.content)
            self.image_data[url] = Image.open(image_data).resize((100, 100))
        
    def update_ui(self, mod_data):
        self.fetch_image_data(mod_data)
        
        for widget in self.frame.winfo_children():
            widget.destroy()
        
        for mod in mod_data:
            mod_frame = ctk.CTkFrame(self.frame, border_width=2)
            mod_frame.pack(padx=10, pady=5, fill="x", expand=True)
            
            mod_name = mod['title']
            author = mod['author']
            icon_url = mod['icon_url']
            image = self.image_data[icon_url]
            photo = ImageTk.PhotoImage(image)
            image_label = ctk.CTkLabel(mod_frame,text="", image=photo)
            image_label.image = photo  # Keep a reference to avoid garbage collection
            image_label.pack(anchor="w")
            mod_name_label = ctk.CTkLabel(mod_frame, text=f"Mod Name: {mod_name}", font=('Arial', 12, 'bold'))
            mod_name_label.pack(anchor="w")
            
            author_label = ctk.CTkLabel(mod_frame, text=f"Author: {author}", font=('Arial', 10, 'italic'))
            author_label.pack(anchor="w")
            download_button = ctk.CTkButton(
                mod_frame,
                text="Download",
                font=('Arial', 10, 'bold'),
                command=lambda m=mod: download_mod(self.server_data, mod_data=m)
            )
            download_button.pack(anchor="w")
            # Render image using stored image data
            # image = self.image_data[icon_url]
            # photo = ImageTk.PhotoImage(image)
            # image_label = ctk.CTkLabel(mod_frame,text="", image=photo)
            # image_label.image = photo  # Keep a reference to avoid garbage collection
            # image_label.pack(anchor="w")
        
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))



def mod_menu(server_info):
    mod_loader = server_info["modloader"]
    game_version = server_info["gameVersion"]
    app = ModFetcherApp(mod_loader,game_version,server_info)
    app.mainloop()

if __name__ == "__main__":
    setup_logging("modmenu2.log")
    app = ModFetcherApp("fabric","1.18.2",None)
    app.mainloop()
