# Disclaimer 1
# This code is taken from the ForgePY project(https://github.com/matejmajny/forgePY/tree/main) under the GPL-3.0 license(https://github.com/matejmajny/forgePY/tree/main?tab=GPL-3.0-1-ov-file#readme)
# And modified to suite my needs. I claim no credit or ownership for this code in forge.py
# 20/05/2024
# End of Disclaimer 1
from bs4 import BeautifulSoup
import requests
import os
import tkinter as tk
import threading as Thread
import subprocess
from tkinter import messagebox
from file_utils.path_management import adjust_path
from config.errors import err_code_process_closed
from file_utils.path_management import adjust_path
import re
list = []

# The code falls under Disclaimer 1
def request(version):
    version = str(version)
    url = f"https://files.minecraftforge.net/net/minecraftforge/forge/index_{version}.html"
    req = requests.get(url).text
    doc = BeautifulSoup(req, "html.parser")
    tags = doc.find_all(["a"], title="Installer", href=True)
    for a in tags:
        list.append(a["href"])
# The code falls under Disclaimer 1
def GetLatestURL(version):
    request(version)
    latestURL = str(list[0])
    latestURL = latestURL[latestURL.find("&")+5:]
    return latestURL
# The code falls under Disclaimer 1
def GetRecommendedURL(version):
    request(version)
    recommendedURL = str(list[1])
    recommendedURL = recommendedURL[recommendedURL.find("&")+5:]
    return recommendedURL

def extract_forge_libraries_path(file_path: str):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
        
        for line in lines:
            if '@libraries' in line:
                match = re.search(r'@libraries[^\s]*', line)
                if match:
                    libraries_path = match.group(0)
                    return libraries_path

        log("No @libraries path found in the file.")
        return None

    except FileNotFoundError:
        log(f"File {file_path} not found.")
        return None
    except Exception as e:
        log(f"An error occurred: {e}")
        return None
def run_command(command, output_widget):
        log(command)
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        for line in iter(process.stdout.readline, ""):
            output_widget.insert(tk.END, line)
            output_widget.see(tk.END)
            if "The server installed successfully" in line:
                output_widget.insert(tk.END, "\nInstallation complete.Close the window to continue\n")
                output_widget.see(tk.END)
                messagebox.showinfo("Installation complete","The installation is complete. You must close the window to continue")
                # if root and root.winfo_exists():  # Check if root window exists
                    # log("ROOT")
                
        process.stdout.close()
        process.wait()


def install_forge_server(jar_file,name):
    root = tk.Tk()
    root.title("Installing Server")

    output_widget = tk.Text(root, wrap="word")
    output_widget.pack(expand=True, fill="both")
    use_name = name.replace(" ","")
    os.chdir(f"./servers/{use_name}")
    jar_file_main = f'forge_installer_{jar_file}.jar'
    command = ["java", "-jar", jar_file_main, "--installServer"]
    thread = Thread.Thread(target=run_command, args=(command, output_widget))
    thread.start()
    root.mainloop()

def run_forge_server(server_info,text_widget,on_finish):
    adjust_path()
    out_p = os.getcwd()
    global process  # Declare process as a global variable
    process = None
    path = server_info.get('path', "/fake/")
    java = server_info.get('javaPath', "java")
    java = os.path.join(out_p, java)
    os.chdir(path)
    log(os.getcwd())
    lib = extract_forge_libraries_path("run.bat")
    jar = ""
    if(lib is None):
        game_v = server_info.get('gameVersion', "0.0")
        lib = f"minecraft_server.{game_v}.jar"
        log(lib)
        jar = "-jar"
    ram = server_info.get('ram', "2G")
    
    cmd = f"{java} -Xmx{ram} {jar} {lib} nogui %*"
    def run_command(command):
        global process
        log(command)
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        try:
            for line in iter(process.stdout.readline, ""):
                # log(line)
                formatted_output,color = format_output_as_html(line)
                try:
                    text_widget.insert(tk.END, formatted_output,color)
                    text_widget.see(tk.END)  # Auto-scroll to the end
                except Exception as e:
                    log(e)
            process.stdout.close()
            process.wait()
            process.pid
            on_finish(server_info,text_widget)
        except ValueError:
            name = server_info.get("displayName",'None')
            log(f"{err_code_process_closed}:Server{name} tried to read from stdout when stdout was closed")
            # on_finish(server_info)

    def format_output_as_html(output):
        return f'{output}','error'

    thread = Thread.Thread(target=run_command, args=(cmd,), daemon=True)
    thread.start()
    while(process == None):
        # Wait for the process to become valid
        pass
    adjust_path()
    return process
