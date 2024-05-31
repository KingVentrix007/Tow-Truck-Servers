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
from config.ui_config import default_color,make_mods_pretty
import urllib.request
import markdown
from tkhtmlview import HTMLLabel
def download_image(url, size=(150, 150)):
    response = requests.get(url)
    response.raise_for_status()  # Check if the request was successful
    image_data = response.content
    image = Image.open(BytesIO(image_data))
    image = image.resize(size)  # Resize the image to the given size
    return ImageTk.PhotoImage(image)
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
def find_mod_id(json_path, filename):
    if(json_path == None):
        return None
    try:
        
        with open(json_path, 'r') as file:
            json_data = file.read()
    except FileNotFoundError:
        log(f"Error: JSON file '{json_path}' not found.")
        return None

    try:
        mods = json.loads(json_data)["mods"]
        log("mods = json.loads(json_data)['mods']",mods)
    except json.JSONDecodeError:
        log(f"Error: Invalid JSON format in file '{json_path}'.")
        return None

    for mod in mods:
        log("for mod in mods:",mod)
        for mod_id, mod_file in mod.items():
            decoded_filename = urllib.parse.unquote(mod_file)
            filename = urllib.parse.unquote(filename)
            # log(decoded_filename,filename)
            if filename == decoded_filename:
                return mod_id
    log(f"No mod found for filename '{filename}' in the provided JSON data.")
    return None



def mod_clicked(mod_data, frame):
    # Clear the frame
    for widget in frame.winfo_children():
        widget.destroy()
    
    body_data = apiv2.get_project_data_id(mod_data["project_id"])
    print("Clicked mod " + str(body_data))
    html_body = None#body_data.get("body", None)
    mod_name = mod_data["title"]
    mod_icon_url = mod_data["icon_url"]
    author = mod_data["author"]
    description = mod_data.get("description", "None")
    gallery = mod_data.get("gallery", [])
    
    # Display mod data in frame
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    
    # Mod Icon
    if mod_icon_url:
        try:
            mod_icon_image = download_image(mod_icon_url, size=(200, 200))
            mod_icon_label = ctk.CTkLabel(frame, text="", image=mod_icon_image)
            mod_icon_label.image = mod_icon_image  # Keep a reference to avoid garbage collection
            mod_icon_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
        except Exception as e:
            print(f"Failed to load image from {mod_icon_url}: {e}")
    
    # Mod Name
    mod_name_label = ctk.CTkLabel(frame, text=mod_name, font=("Helvetica", 16, "bold"))
    mod_name_label.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="w")
    
    # Author
    author_label = ctk.CTkLabel(frame, text=f"Author: {author}", font=("Helvetica", 14))
    author_label.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="w")
    
    # Description
    description_label = ctk.CTkLabel(frame, text=description, font=("Helvetica", 12), wraplength=400, justify="left")
    description_label.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="w")
    
    # Display Markdown Body
    if html_body:
        # Convert Markdown to HTML
        html_content = markdown.markdown(html_body)
        
        # Display HTML content
        html_frame = ctk.CTkFrame(frame)
        html_frame.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="w")
        html_label = HTMLLabel(html_frame, html=html_content)
        html_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
    
    # Gallery
    gallery_frame = ctk.CTkFrame(frame)
    gallery_frame.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky="w")

    def load_and_render_image(image_url, row, col):
        try:
            gallery_image = download_image(image_url, size=(200, 200))
            gallery_label = ctk.CTkLabel(gallery_frame, text="", image=gallery_image)
            gallery_label.image = gallery_image  # Keep a reference to avoid garbage collection
            gallery_label.grid(row=row, column=col, padx=5, pady=5)
        except Exception as e:
            print(f"Failed to load image from {image_url}: {e}")

    def load_gallery_images():
        for i, image_url in enumerate(gallery):
            # print("image_url == ",image_url)
            Thread(target=load_and_render_image, args=(image_url, i//3, i%3)).start()
    
    if gallery:
        load_gallery_images()
    
    # Adjust column weights for better spacing
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_columnconfigure(1, weight=1)

def download_mod(mod_data, server_info):
    print("Downloading mod")
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
    if(len(mod_data) <= 0):
        return None
    return mod_data_info

# def download_mod(server_data,mod_data):
#     mod_name = mod_data["title"]
#     print(f"Downloading mod: {mod_name}")
def clear_canvas(canvas):
    # Iterate through all children of the canvas and destroy them
    for widget in canvas.winfo_children():
        widget.destroy()
def display_mod_files(mod_list_frame,mod_path,json_path):
        for widget in mod_list_frame.winfo_children():
            widget.destroy()
        
        mod_files = [f for f in os.listdir(mod_path) if f.endswith('.jar') or f.endswith('.disabled')]
        log(mod_files)
        for mod in mod_files:
            mod_id = find_mod_id(json_path, mod)
            log("mod_id",mod_id)
            if mod_id != None:
                name = apiv2.id_to_name(mod_id)
            else:
                name = None
            log(mod)
            if(name != None ):
                label = ctk.CTkLabel(mod_list_frame, text=name,text_color="cyan",bg_color=default_color,fg_color=default_color)
            else:
                label = ctk.CTkLabel(mod_list_frame, text=mod,text_color="cyan",bg_color=default_color,fg_color=default_color)
            label.pack(anchor='w', padx=10, pady=2)
class ModFetcherApp(ctk.CTkToplevel):
    def __init__(self, loader, version, server_info):
        super().__init__()
        self.title("Mod Fetcher")
        self.geometry("800x400")  # Increased width to accommodate two frames side by side
        self.mod_loader = loader
        self.game_version = version
        self.server_data = server_info
        self.search_var = tk.StringVar()
        
        self.search_entry = ctk.CTkEntry(self, textvariable=self.search_var)
        self.search_entry.pack(pady=10)
        
        self.search_button = ctk.CTkButton(self, text="Search", command=self.on_search_clicked)
        self.search_button.pack()
        
        # Create two canvases: search_canvas and file_canvas
        self.search_canvas = ctk.CTkCanvas(self)
        self.file_canvas = ctk.CTkCanvas(self)
        self.mod_view_canvas = ctk.CTkCanvas(self)

        # Create frames within the canvases
        self.search_frame = ctk.CTkFrame(self.search_canvas)
        self.file_frame = ctk.CTkFrame(self.file_canvas)
        self.mod_view_frame = ctk.CTkFrame(self.mod_view_canvas)
        # Create scrollbars for each canvas
        self.search_scrollbar = ctk.CTkScrollbar(self, orientation="vertical", command=self.search_canvas.yview)
        self.file_scrollbar = ctk.CTkScrollbar(self, orientation="vertical", command=self.file_canvas.yview)
        self.mod_view_scrollbar = ctk.CTkScrollbar(self, orientation="vertical", command=self.mod_view_canvas.yview)

        self.search_canvas.configure(yscrollcommand=self.search_scrollbar.set, bg=default_color, borderwidth=5)
        self.file_canvas.configure(yscrollcommand=self.file_scrollbar.set, bg=default_color, borderwidth=5)
        self.mod_view_canvas.configure(yscrollcommand=self.mod_view_scrollbar.set,bg=default_color,background=default_color, borderwidth=5)
        # Pack the scrollbars and canvases
        self.search_scrollbar.pack(side="right", fill="y")
        self.search_canvas.pack(side="right", fill="both", expand=True)
        

        self.file_canvas.pack(side="left", fill="both", expand=True)
        self.file_scrollbar.pack(side="left", fill="y")
        
        self.mod_view_scrollbar.pack(side="right", fill="y")
        self.mod_view_canvas.pack(side="right", fill="both", expand=True)
       
        # Add frames to their respective canvases
        self.search_canvas.create_window((0, 0), window=self.search_frame, anchor="nw")
        self.file_canvas.create_window((0, 0), window=self.file_frame, anchor="nw")
        self.mod_view_canvas.create_window((0, 0),window=self.mod_view_frame,anchor="nw")

        self.search_frame.bind("<Configure>", self.on_frame_configure_search)
        self.file_frame.bind("<Configure>", self.on_frame_configure_file)
        self.mod_view_frame.bind("<Configure>", self.on_frame_configure_mod)
        
        # Dictionary to store image data
        self.image_data = {}
        # self.status_label = ctk.CTkLabel(self.search_frame, text="")
        # self.status_label.pack(side=ctk.TOP)
        
        mod_path = os.path.normpath(os.path.join(server_info["path"], "mods"))
        json_path = os.path.join(server_info["path"], "towtruckconfig.json")
        display_files_thread = Thread(target=display_mod_files, args=(self.file_frame, mod_path, json_path))
        display_files_thread.start()
        
    def on_search_clicked(self):
        query = self.search_var.get()
        self.search_button.configure(state="disabled")
        self.search_entry.configure(state="disabled")
        self.update_mod_data(query)
        
    def update_mod_data(self, query):
        thread = Thread(target=self.fetch_mod_data, args=(query,))
        thread.start()
        
    def fetch_mod_data(self, query=None):
        self.status_label = ctk.CTkLabel(self.search_frame, text="")
        self.status_label.pack(side=ctk.TOP)        
        self.status_label.configure(text="Searching for mods...")
        mod_data = get_mod_data(query, self.mod_loader, self.game_version)
        self.update_ui(mod_data)
        
    def fetch_image_data(self, mod_data):
        for mod in mod_data:
            url = mod['icon_url']
            response = requests.get(url)
            image_data = BytesIO(response.content)
            self.image_data[url] = Image.open(image_data).resize((100, 100))
        
    def update_ui(self, mod_data):
        if(mod_data != None):
            if make_mods_pretty:
                self.status_label.configure(text="Prettifying output...")
                self.fetch_image_data(mod_data)
            
            for widget in self.search_frame.winfo_children():
                widget.destroy()
            
            for mod in mod_data:
                mod_frame = ctk.CTkFrame(self.search_frame, border_width=2, border_color="grey")
                mod_frame.pack(padx=10, pady=5, fill=ctk.BOTH, expand=True)  # Expands vertically to fill extra space
                
                mod_name = mod['title']
                author = mod['author']
                if make_mods_pretty:
                    icon_url = mod['icon_url']
                    image = self.image_data[icon_url]
                    photo = ImageTk.PhotoImage(image)
                    image_label = ctk.CTkLabel(mod_frame, text="", image=photo)
                    image_label.image = photo  # Keep a reference to avoid garbage collection
                    image_label.pack(side="top")  # Align at the top of the frame
                
                mod_name_label = ctk.CTkLabel(mod_frame, text=f"Mod Name: {mod_name}", font=('Arial', 12, 'bold'))
                mod_name_label.pack(side="top")  # Align at the top of the frame
                
                author_label = ctk.CTkLabel(mod_frame, text=f"Author: {author}", font=('Arial', 10, 'italic'))
                author_label.pack(side="top")  # Align at the top of the frame
                
                download_button = ctk.CTkButton(
                    mod_frame,
                    text="Download",
                    font=('Arial', 10, 'bold'),
                    command=lambda m=mod: download_mod(mod_data=m, server_info=self.server_data)
                )
                download_button.pack(side="top")  # Align at the top of the frame
                mod_frame.bind("<Button-1>", lambda event, m=mod: mod_clicked(mod_data=m,frame=self.mod_view_frame))
        else:
            self.status_label.configure(text="No results found")
        self.search_canvas.configure(scrollregion=self.search_canvas.bbox("all"))
        self.search_button.configure(state="normal")
        self.search_entry.configure(state="normal")

    def on_frame_configure_search(self, event):
        self.search_canvas.configure(scrollregion=self.search_canvas.bbox("all"))
    
    def on_frame_configure_file(self, event):
        self.file_canvas.configure(scrollregion=self.file_canvas.bbox("all"))
    def on_frame_configure_mod(self, event):
        self.mod_view_canvas.configure(scrollregion=self.mod_view_canvas.bbox("all"))



def mod_menu(server_info):
    mod_loader = server_info["modloader"]
    game_version = server_info["gameVersion"]
    app = ModFetcherApp(mod_loader,game_version,server_info)
    app.mainloop()

if __name__ == "__main__":
    setup_logging("modmenu2.log")
    app = ModFetcherApp("fabric","1.18.2",None)
    app.mainloop()
