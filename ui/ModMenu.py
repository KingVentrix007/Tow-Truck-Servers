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
from mods.files import get_mod_name_from_jar,mod_already_installed
mod_list_frame_g = None
file_canvas_g = None
current_offset = 0
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
                    print( progress["value"] )
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
        return None,None
    try:
        
        with open(json_path, 'r') as file:
            json_data = file.read()
    except FileNotFoundError:
        log(f"Error: JSON file '{json_path}' not found.")
        return None,None

    try:
        mods = json.loads(json_data)["mods"]
        log("mods = json.loads(json_data)['mods']",mods)
    except json.JSONDecodeError:
        log(f"Error: Invalid JSON format in file '{json_path}'.")
        return None,None

    for mod in mods:
        log("for mod in mods:",mod)
        for mod_id, mod_data in mod.items():
            mod_file = mod_data["filename"]
            image = mod_data["icon"]
            decoded_filename = urllib.parse.unquote(mod_file)
            filename = urllib.parse.unquote(filename)
            # log(decoded_filename,filename)
            if filename == decoded_filename:
                return mod_id,image
    log(f"No mod found for filename '{filename}' in the provided JSON data.")
    return None,None



def mod_clicked_thread(mod_data,frame):
    # global file_canvas_g
    # clear_canvas(file_canvas_g)
    mod_thread =  Thread(target=mod_clicked, args=(mod_data,frame))
    mod_thread.start()

def mod_clicked(mod_data, frame):
    # Clear the frame
    for widget in frame.winfo_children():
        widget.destroy()
    
    # body_data = apiv2.get_project_data_id(mod_data["project_id"])
    # # print("Clicked mod " + str(body_data))

    mod_name = mod_data["title"]
    mod_icon_url = mod_data["icon_url"]
    author = mod_data["author"]
    description = mod_data.get("description", "None")
    gallery = mod_data.get("gallery", [])
    # print("Keys",mod_data.keys())
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
    author_data = apiv2.get_user_data(author)
    if(author_data is not None):
        avatar_url = author_data["avatar_url"]
        if(avatar_url is not None):
            avatar_url_image = download_image(avatar_url, size=(50, 50))
            avatar_url_label = ctk.CTkLabel(frame,image=avatar_url_image,text="")
            avatar_url_label.image = avatar_url_image
            avatar_url_label.grid(row=2, column=0,columnspan=2, padx=10, pady=5, sticky="w")
    author_label = ctk.CTkLabel(frame, text=f"Author: {author}", font=("Helvetica", 14))
    author_label.grid(row=2, column=1, columnspan=2, padx=0, pady=5, sticky="w")
    
    # Description
    description_label = ctk.CTkLabel(frame, text=description, font=("Helvetica", 12), wraplength=400, justify="left")
    description_label.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="w")
    
    # Display Markdown Body
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
    
    # # Adjust column weights for better spacing
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_columnconfigure(1, weight=1)

def download_mod(mod_data, server_info):
    print("Downloading mod")
    mod_path = os.path.join(server_info["path"], "mods")
    mod_name = mod_data["title"]
    # ensure_config_exists(config_path)
    # config = load_config(config_path)   
    # if mod_id not in [mod_id for mod in config["mods"] for mod_id in mod.keys()]:
    #     pass
    # else:
    #     log(f"Mod {mod_id} is already installed, skipping download.")
    #     print(f"Mod {mod_id} is already installed, skipping download.")
    #     return

    waiting_window = show_waiting_window(mod_data.get("title"))

    def download_mod_files():
        # nonlocal config

        urls = fetch_mod_urls(mod_data, server_info)
        if(urls == None):
            messagebox.showerror("Failed to get mod urls","Failed to get mod_urls, please report this error, with the mod name, server version and mod loader")
        else:
            url = urls["url"]
            mod_file_name = os.path.basename(url)
            installed_mods = [f for f in os.listdir(mod_path) if f.endswith('.jar') or f.endswith('.disabled')]
            if(mod_already_installed(mod_file_name,installed_mods)):
                print(f"Mod {mod_name} is already installed. Skipping mod")
                return
            # mod_info = {"filename": mod_file_name,"icon": mod_data.get("icon_url",None)}
            # config["mods"].append({mod_id: mod_info})
            # save_config(config_path, config)

            dependencies = urls["dependencies"]
            close_waiting_window(waiting_window)
            mod_folder = os.path.normpath(os.path.join(server_info.get("path", ""), "mods"))
            os.makedirs(mod_folder, exist_ok=True)

            root = tk.Tk()
            root.title("Download Progress")
            label = ttk.Label(root, text=f"Downloading mod {mod_name}...")
            label.pack(pady=10)
            progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
            progress.pack(pady=10)

            def start_download():
                local_filename = os.path.join(mod_folder, mod_file_name)
                download_file(url, local_filename, progress, root, label, callback=lambda: download_dependencies(dependencies, None, None, mod_folder, progress, root, label))
                log(f"Downloaded mod to {local_filename}")

            Thread(target=start_download).start()
            root.mainloop()
            

    Thread(target=download_mod_files).start()
def download_dependencies(dependencies, config, config_path, mod_folder, progress, root, label):
    label.config(text="Mod download complete! Downloading dependencies...")
    for dep in dependencies:
        dep_id = dep["id"]
        dep_url = dep["url"]
        dep_file = os.path.basename(dep_url)
        
        installed_mods = [f for f in os.listdir(mod_folder) if f.endswith('.jar') or f.endswith('.disabled')]
        if(mod_already_installed(dep_file,installed_mods)):
            print(f"Dependencies already installed {dep_file}")
        else:
            log(f"dependencies {dep_id} url: {dep_url}" )
            dep_file_name = os.path.basename(dep_url)
            local_dep_filename = os.path.join(mod_folder, dep_file_name)
            download_file(dep_url, local_dep_filename, progress, root, label)
        #     dep_info = {"filename":dep_file_name,"icon":None}
        #     config["mods"].append({dep_id: dep_info})
        #     save_config(config_path, config)
        # # else:
        #     log(f"Dependency {dep_id} already exists, skipping download.")
    label.config(text="All downloads complete!")
    log("Downloaded all dependencies.")
    root.destroy()
def get_mod_data(query=None,loaders="forge",version="1.19.2",initial_offset=0):
    global current_offset
    
    print("Searching,,,")
    # Simulate retrieving data based on the query
    mod_data_info,ids = apiv2.search_mods_internal(query=query,modloader=loaders,version=version,initial_offset=initial_offset)
    if(len(mod_data_info) <= 0):
        return None
    return mod_data_info

def clear_canvas(canvas):
    # Iterate through all children of the canvas and destroy them
    for widget in canvas.winfo_children():
        widget.destroy()

def delete_mod_file(mod_file_path,mod_path,json_path):
    global mod_list_frame_g
    try:
        os.remove(mod_file_path)
        log(f"Deleted {mod_file_path}")
        # Refresh the mod list after deletion
        display_mod_files(mod_list_frame_g, mod_path, json_path)
    except Exception as e:
        log(f"Failed to delete {mod_file_path}: {e}")

def display_mod_files(mod_list_frame, mod_path, json_path):
    global mod_list_frame_g
    mod_list_frame_g = mod_list_frame

    for widget in mod_list_frame.winfo_children():
        widget.destroy()

    mod_files = [f for f in os.listdir(mod_path) if f.endswith('.jar') or f.endswith('.disabled')]
    log(mod_files)
    number_of_mods_frame = ctk.CTkFrame(mod_list_frame, width=400, height=110, border_width=5)
    number_of_mods_frame.pack(pady=4, padx=10, anchor='w')
    number_of_mods = len(mod_files)
    number_of_mods_label = ctk.CTkLabel(number_of_mods_frame,text=f"You have {number_of_mods} mods installed")
    number_of_mods_label.pack(side=ctk.TOP)
    for mod in mod_files:
        mod_to_decode = os.path.join(mod_path, mod)
        mod_name, method, match, decoded_file_name = get_mod_name_from_jar(mod_to_decode)
        print("Name from jar: %s" % mod_name, "|", method, "|", mod)
        
        if match:
            name_to_find = mod_name
            icon_url, name = apiv2.get_mod_icon(name_to_find)
        elif decoded_file_name is not None:
            name_to_find = decoded_file_name
            print(name_to_find)
            icon_url, name = apiv2.get_mod_icon(name_to_find)
        else:
            name = mod
            icon_url = None
        
        internal_frame = ctk.CTkFrame(mod_list_frame, width=400, height=110, border_width=5)
        internal_frame.pack(pady=4, padx=10, anchor='w')

        if icon_url:
            print("Loading icon url for ", name)
            try:
                print("Image is ", icon_url)
                response = requests.get(icon_url, stream=True)
                response.raise_for_status()
                image = Image.open(response.raw)
                image = image.resize((100, 100))
                photo = ImageTk.PhotoImage(image)

                icon_label = ctk.CTkLabel(internal_frame, image=photo, text="")
                icon_label.image = photo  # Keep a reference to avoid garbage collection
                icon_label.pack(anchor='w', padx=10, pady=2, side="left")
            except Exception as e:
                print(f"Failed to load image from {icon_url}: {e}")
                fallback_image(internal_frame)
        else:
            fallback_image(internal_frame)

        label_name = ctk.CTkLabel(internal_frame, text=name, text_color="cyan", bg_color="#333333", fg_color="#333333", width=200, height=110)
        label_name.pack(anchor='w', padx=10, pady=2, side="left")

        delete_button = ctk.CTkButton(internal_frame, text="Delete", command=lambda m=mod_to_decode: delete_mod_file(m,mod_path,json_path))
        delete_button.pack(anchor='e', padx=10, pady=2, side="right")

def fallback_image(internal_frame):
    print("Fallback image")
    image = Image.open("./assets/images/package.png")
    image = image.resize((100, 100))
    photo = ImageTk.PhotoImage(image)

    icon_label = ctk.CTkLabel(internal_frame, image=photo, text="")
    icon_label.image = photo  # Keep a reference to avoid garbage collection
    icon_label.pack(anchor='w', padx=10, pady=2, side="left")
class ModFetcherApp(ctk.CTkToplevel):
    def __init__(self, loader, version, server_info):
        super().__init__()
        global file_canvas_g
        self.title("Mod Fetcher")
        self.geometry("1088x500")  #
        self.minsize(width=1088, height=500)#ncreased width to accommodate two frames side by side
        self.mod_loader = loader
        self.game_version = version
        self.server_data = server_info
        self.search_var = tk.StringVar()
        
        self.search_entry = ctk.CTkEntry(self, textvariable=self.search_var)
        self.search_entry.pack(pady=10)
        self.search_bar = ctk.CTkFrame(self)
        self.search_button = ctk.CTkButton(self.search_bar, text="Search", command=self.on_search_clicked)
        
        self.next_button = ctk.CTkButton(self.search_bar,text="Next", command=self.next_mods)
        self.next_button.pack(side=ctk.LEFT,padx=2)
        self.search_button.pack(side=ctk.LEFT,padx=2)
        self.back_button = ctk.CTkButton(self.search_bar,text="Back", command=self.back_mods)
        self.back_button.pack(side=ctk.LEFT,padx=2)
        self.search_bar.pack()
        # Create two canvases: search_canvas and file_canvas
        self.search_canvas = ctk.CTkCanvas(self)
        self.file_canvas = ctk.CTkCanvas(self)
        file_canvas_g = self.file_canvas
        # self.mod_view_canvas = ctk.CTkCanvas(self)

        # Create frames within the canvases
        self.search_frame = ctk.CTkFrame(self.search_canvas)
        self.file_frame = ctk.CTkFrame(self.file_canvas)
        # self.mod_view_frame = ctk.CTkFrame(self.mod_view_canvas)
        # Create scrollbars for each canvas
        self.search_scrollbar = ctk.CTkScrollbar(self, orientation="vertical", command=self.search_canvas.yview)
        self.file_scrollbar = ctk.CTkScrollbar(self, orientation="vertical", command=self.file_canvas.yview)
        # self.mod_view_scrollbar = ctk.CTkScrollbar(self, orientation="vertical", command=self.mod_view_canvas.yview)

        self.search_canvas.configure(yscrollcommand=self.search_scrollbar.set, bg=default_color, borderwidth=5)
        self.file_canvas.configure(yscrollcommand=self.file_scrollbar.set, bg=default_color, borderwidth=5)
        # self.mod_view_canvas.configure(yscrollcommand=self.mod_view_scrollbar.set,bg=default_color,background=default_color, borderwidth=5)
        # Pack the scrollbars and canvases
        self.search_scrollbar.pack(side="right", fill="y")
        self.search_canvas.pack(side="right", fill="both", expand=True)
        

        self.file_canvas.pack(side="left", fill="both", expand=True)
        self.file_scrollbar.pack(side="left", fill="y")
        
        # self.mod_view_scrollbar.pack(side="right", fill="y")
        # self.mod_view_canvas.pack(side="right", fill="both", expand=True)
       
        # Add frames to their respective canvases
        self.search_canvas.create_window((0, 0), window=self.search_frame, anchor="nw")
        self.file_canvas.create_window((0, 0), window=self.file_frame, anchor="nw")
        # self.mod_view_canvas.create_window((0, 0),window=self.mod_view_frame,anchor="nw")

        self.search_frame.bind("<Configure>", self.on_frame_configure_search)
        self.file_frame.bind("<Configure>", self.on_frame_configure_file)
        # self.mod_view_frame.bind("<Configure>", self.on_frame_configure_mod)
        
        # Dictionary to store image data
        self.image_data = {}
        # self.status_label = ctk.CTkLabel(self.search_frame, text="")
        # self.status_label.pack(side=ctk.TOP)
        
        mod_path = os.path.normpath(os.path.join(server_info["path"], "mods"))
        json_path = os.path.join(server_info["path"], "towtruckconfig.json")
        self.on_search_clicked()
        display_files_thread = Thread(target=display_mod_files, args=(self.file_frame, mod_path, json_path))
        display_files_thread.start()
    
    def on_search_clicked(self):
        query = self.search_var.get()
        self.search_button.configure(state="disabled")
        self.search_entry.configure(state="disabled")
        self.next_button.configure(state="disabled")
        self.back_button.configure(state="disabled")
        
        self.update_mod_data(query)
    def next_mods(self):
        global current_offset
        current_offset = current_offset+20
        self.search_button.configure(state="disabled")
        self.search_entry.configure(state="disabled")
        self.next_button.configure(state="disabled")
        self.back_button.configure(state="disabled")
        query = self.search_var.get()
        self.offset = current_offset
        
        clear_canvas(self.search_frame)
        print(f"Current offset self.offset == {self.offset}")
        self.update_mod_data(query=query,offset=self.offset)
    def back_mods(self):
        global current_offset
        current_offset = current_offset-20
        self.search_button.configure(state="disabled")
        self.search_entry.configure(state="disabled")
        self.next_button.configure(state="disabled")
        self.back_button.configure(state="disabled")
        query = self.search_var.get()
        self.offset = current_offset
        
        clear_canvas(self.search_frame)
        print(f"Current offset self.offset == {self.offset}")
        self.update_mod_data(query=query,offset=self.offset)
        
        # search_for_mods(self.server_data, self.search_var.get(), self.search_frame, self.search_button,offset_to_use=current_offset)
    def update_mod_data(self, query,offset=0):
        thread = Thread(target=self.fetch_mod_data, args=(query,offset,))
        thread.start()
        
    def fetch_mod_data(self, query=None,offset=0):
        
        self.status_label = ctk.CTkLabel(self.search_frame, text="")
        self.status_label.pack(side=ctk.TOP)        
        self.status_label.configure(text="Searching for mods...")
        print("Searching for mods with offset %d...", offset)
        mod_data = get_mod_data(query, self.mod_loader, self.game_version,offset)
        self.update_ui(mod_data)
        
    def fetch_image_data(self, mod_data):
        try:
            for mod in mod_data:
                url = mod['icon_url']
                
                response = requests.get(url)
                image_data = BytesIO(response.content)
                self.image_data[url] = Image.open(image_data).resize((100, 100))
        except Exception as e:
            return None
        
    def update_ui(self, mod_data):
        if mod_data is not None:
            if make_mods_pretty:
                self.status_label.configure(text="Prettifying output...")
                self.fetch_image_data(mod_data)

            for widget in self.search_frame.winfo_children():
                widget.destroy()

            for mod in mod_data:
                mod_frame = ctk.CTkFrame(self.search_frame, border_width=2, border_color="grey", height=200, width=200)
                mod_frame.pack(padx=10, pady=5, fill=ctk.BOTH, expand=True)

                mod_name = mod['title']
                author = mod['author']
                description = mod.get('description', 'No description available')
                categories = ", ".join(mod["display_categories"])
                downloads = mod["downloads"]
                follows = mod["follows"]
                date_modified = mod["date_modified"]

                if make_mods_pretty:
                    try:
                        icon_url = mod['icon_url']
                        image = self.image_data[icon_url]
                    except KeyError:
                        image = None
                    if image is not None:
                        photo = ImageTk.PhotoImage(image)
                    else:
                        image = Image.open("./assets/images/package.png")
                        image = image.resize((100, 100))
                        photo = ImageTk.PhotoImage(image)

                    image_label = ctk.CTkLabel(mod_frame, text="", image=photo)
                    image_label.image = photo  # Keep a reference to avoid garbage collection
                    image_label.grid(row=0, column=0, rowspan=6, padx=5, pady=5, sticky='n')  # Position at the top left

                mod_name_label = ctk.CTkLabel(mod_frame, text=f"{mod_name}", font=('Arial', 14, 'bold'))
                mod_name_label.grid(row=0, column=1, columnspan=2, sticky='w')

                author_label = ctk.CTkLabel(mod_frame, text=f"By: {author}", font=('Arial', 12, 'italic'))
                author_label.grid(row=1, column=1, columnspan=2, sticky='w')

                description_label = ctk.CTkLabel(mod_frame, text=f"{description}", font=('Arial', 12),wraplength=300)
                description_label.grid(row=2, column=1, columnspan=2, sticky='w')

                categories_label = ctk.CTkLabel(mod_frame, text=f"Categories: {categories}", font=('Arial', 12),wraplength=300)
                categories_label.grid(row=3, column=1, columnspan=2, sticky='w')

                info_label = ctk.CTkLabel(mod_frame, text=f"Downloads: {downloads} | Follows: {follows} | Last Modified: {date_modified}", font=('Arial', 12))
                info_label.grid(row=4, column=0, columnspan=2, sticky='w', padx=5, pady=5)

                download_button = ctk.CTkButton(
                    mod_frame,
                    text="Download",
                    font=('Arial', 12, 'bold'),
                    command=lambda m=mod: download_mod(mod_data=m, server_info=self.server_data)
                )
                download_button.grid(row=5, column=0, columnspan=2, sticky='w', padx=10)

                mod_frame.grid_columnconfigure(2, weight=1)  # Ensure column 2 takes up extra space

        else:
            self.status_label.configure(text="No results found")

        self.search_canvas.configure(scrollregion=self.search_canvas.bbox("all"))
        self.search_button.configure(state="normal")
        self.search_entry.configure(state="normal")
        self.next_button.configure(state="normal")
        self.back_button.configure(state="normal")


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
