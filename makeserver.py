# this is the makeserver file, can u do the same:
import re
import forgepy
import requests
import os
import tkinter as tk
from tkinter import ttk
from threading import Thread
import subprocess
import json
from tkinter import messagebox
import psutil
def download_server_jar(name:str, version:str, progress_var, on_complete):
    latest = forgepy.GetLatestURL(version) # This must always have the version var past to it. 
    response = requests.get(latest, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024 # 1 Kibibyte
    bytes_so_far = 0
    use_name = name.replace(" ","")
    with open(f"./servers/{use_name}/forge_installer_{version}.jar", "wb") as file:
        for data in response.iter_content(block_size):
            file.write(data)
            bytes_so_far += len(data)
            progress = int(bytes_so_far * 100 / total_size)
            progress_var.set(progress)
    on_complete(name, version)

def install_server(name:str, version:str, root,eula=False):
    def run_command(command, output_widget):
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        for line in iter(process.stdout.readline, ""):
            output_widget.insert(tk.END, line)
            output_widget.see(tk.END)
            if "The server installed successfully" in line:
                output_widget.insert(tk.END, "\nInstallation complete.Close the window\n")
                output_widget.see(tk.END)
                messagebox.showinfo("Installation complete","The installation is complete. You must close the window to continue")
                # if root and root.winfo_exists():  # Check if root window exists
                    # print("ROOT")
                
        process.stdout.close()
        process.wait()

    def run_server(name:str):
        # if(eula == True):
        #     file = open("eula.txt","w")
        #     file.write()
        server = get_server(name)
        java = server["javaPath"]
    
        ram = server["ram"]
        server_path = server["path"]
        use_path = "."
        if(server_path[0] != "."):
            use_path = use_path + server_path
            os.chdir(use_path)
        else:
            os.chdir(server_path)
        lib = extract_libraries_path(f"run.bat")
        cmd = f"{java} -Xmx{ram} {lib} %*"
        
        root = tk.Tk()
        root.title("Running Server")
        
        output_widget = tk.Text(root, wrap="word")
        output_widget.pack(expand=True, fill="both")
    
        def run_command(command, output_widget):
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
            output_widget.insert(tk.END,"READ THIS:\n")
            
            output_widget.insert(tk.END,os.getcwd())
            output_widget.insert(tk.END,command+"\n\n\n")

            for line in iter(process.stdout.readline, ""):
                output_widget.insert(tk.END, line)
                output_widget.see(tk.END)
                if("EULA" in line):
                    messagebox.showwarning("EULA",f"Open the {server_path}/eula.txt and set it to TRUE, then run the server to continue")
            process.stdout.close()
            process.wait()
        
        thread = Thread(target=run_command, args=(cmd, output_widget))
        thread.start()
        
        root.mainloop()
    def install(name, version):
        root = tk.Tk()
        root.title("Installing Server")

        output_widget = tk.Text(root, wrap="word")
        output_widget.pack(expand=True, fill="both")
        use_name = name.replace(" ","")
        os.chdir(f"./servers/{use_name}")
        jar_file = f"forge_installer_{version}.jar"
        command = ["java", "-jar", jar_file, "--installServer"]
        thread = Thread(target=run_command, args=(command, output_widget))
        thread.start()
        # file = open(f"./servers/{name}/towtruck.cfg")
        root.mainloop()

    install(name, version)
    print("Done install")
    os.chdir("../..")

    add_entry(name, version)
    # os.chdir("../..")
    run_server(name)
    os.chdir("../..")
def extract_libraries_path(file_path: str):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
        
        for line in lines:
            if '@libraries' in line:
                match = re.search(r'@libraries[^\s]*', line)
                if match:
                    libraries_path = match.group(0)
                    return libraries_path

        print("No @libraries path found in the file.")
        return None

    except FileNotFoundError:
        print(f"File {file_path} not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
def get_server(display_name: str, config_path='config.json'):
    # Load existing config
    try:
        with open(config_path, 'r') as file:
            config = json.load(file)
    except FileNotFoundError:
        print("Config file not found.")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None

    # Search for the server with the specified display name
    for server in config.get('servers', []):
        if server.get('displayName') == display_name:
            return server
    
    print(f"Server with display name '{display_name}' not found.")
    return None
def add_entry(name: str, game_version: str, config_path='config.json'):
    display_name = name

    # Retrieve Java version
    try:
        java_version_output = subprocess.check_output(['java', '-version'], stderr=subprocess.STDOUT)
        java_version_output = java_version_output.decode('utf-8')
        java_version = java_version_output.split('\n')[0].split('"')[1]
    except Exception as e:
        print(f"Error retrieving Java version: {e}")
        return

    # Retrieve Java path
    try:
        if os.name == 'nt':  # Windows
            java_path_output = subprocess.check_output(['where', 'java'])
        else:  # Unix-like (Linux, macOS)
            java_path_output = subprocess.check_output(['which', 'java'])
        java_path = java_path_output.decode('utf-8').strip()
    except Exception as e:
        print(f"Error retrieving Java path: {e}")
        return

    # Determine RAM allocation
    total_memory = psutil.virtual_memory().total / (1024 ** 3)  # Convert bytes to GB
    if total_memory > 8:
        allocated_ram = 4
    elif total_memory >= 4:
        allocated_ram = 3
    else:
        allocated_ram = 2
        # Show Tkinter warning
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        messagebox.showwarning("RAM Allocation Warning", "The system has less than 4GB of RAM. The server may experience performance issues.")
        root.destroy()

    # Create new entry
    use_name = name.replace(" ", "")
    new_entry = {
        "displayName": display_name,
        "path": f"./servers/{use_name}",
        "gameVersion": game_version,
        "javaVersion": java_version,
        "javaPath": java_path,
        "ram": f"{allocated_ram}G"
    }

    # Load existing config
    try:
        with open(config_path, 'r') as file:
            config = json.load(file)
    except FileNotFoundError:
        config = {"servers": []}
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return

    # Add new entry to the config
    config['servers'].append(new_entry)

    # Save updated config
    try:
        with open(config_path, 'w') as file:
            json.dump(config, file, indent=4)
        print("New entry added successfully.")
    except Exception as e:
        print(f"Error writing to config file: {e}")
def make_server(name, description, version, seed,eula=False):
    use_name = name.replace(" ","")
    os.makedirs(f"./servers/{use_name}", exist_ok=True)
    
    root = tk.Tk()
    root.title("Downloading Server Jar")
    root.geometry("30x40")
    progress_var = tk.DoubleVar(root, 0.0)
    progressbar = ttk.Progressbar(root, variable=progress_var, maximum=100)
    progressbar.pack(pady=10)
    
    def on_complete(name, version):
        root.destroy()
        install_server(name, version, root)
    
    download_thread = Thread(target=download_server_jar, args=(name, version, progress_var, on_complete))
    download_thread.start()
    
    root.mainloop()

# Example usage:
# make_server("MyServer", "Description", "1.0", "12345")