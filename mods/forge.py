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
from file_utils.path_mangment import adjust_path
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

        print("No @libraries path found in the file.")
        return None

    except FileNotFoundError:
        print(f"File {file_path} not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
def run_command(command, output_widget):
        print(command)
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        for line in iter(process.stdout.readline, ""):
            output_widget.insert(tk.END, line)
            output_widget.see(tk.END)
            if "The server installed successfully" in line:
                output_widget.insert(tk.END, "\nInstallation complete.Close the window to continue\n")
                output_widget.see(tk.END)
                messagebox.showinfo("Installation complete","The installation is complete. You must close the window to continue")
                # if root and root.winfo_exists():  # Check if root window exists
                    # print("ROOT")
                
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







# def run_server():
#             global process  # Ensure process is global
#             adjust_path()

#             path = server_info.get('path', "/fake/")
#             java = server_info.get('javaPath', "java")
#             os.chdir(path)
#             print("PATH == ", os.getcwd())
#             lib = makeserver.extract_libraries_path("run.bat")
#             ram = server_info.get('ram', "2G")
#             cmd = f"{java} -Xmx{ram} {lib} nogui %*"

#             def run_command(command):
#                 global process  # Ensure process is global
#                 print(command)
#                 process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
#                 for line in iter(process.stdout.readline, ""):
#                     print(line)
#                     formatted_output = format_output_as_html(line)
#                     try:
#                         text_widget.insert(tk.END, formatted_output)
#                         text_widget.see(tk.END)  # Auto-scroll to the end
#                     except Exception as e:
#                         pass
#                 process.stdout.close()
#                 process.wait()

#             def format_output_as_html(output):
#                 output = output.replace('ERROR', '[ERROR]')
#                 output = output.replace('WARNING', '[WARNING]')
#                 output = output.replace('INFO', '[INFO]')
#                 return f'{output}'

#             thread = threading.Thread(target=run_command, args=(cmd,), daemon=True)
#             thread.start()
#             print(thread.is_alive())


def run_forge_server(server_info,text_widget):
    global process
    adjust_path()
    path = server_info.get('path', "/fake/")
    java = server_info.get('javaPath', "java")
    os.chdir(path)
    lib = extract_forge_libraries_path("run.bat")
    ram = server_info.get('ram', "2G")
    cmd = f"{java} -Xmx{ram} {lib} nogui %*"
    def run_command(command):
        global process  # Ensure process is global
        print(command)
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        for line in iter(process.stdout.readline, ""):
            print(line)
            formatted_output = format_output_as_html(line)
            try:
                text_widget.insert(tk.END, formatted_output)
                text_widget.see(tk.END)  # Auto-scroll to the end
            except Exception as e:
                print(e)
        process.stdout.close()
        process.wait()

    def format_output_as_html(output):
        output = output.replace('ERROR', '[ERROR]')
        output = output.replace('WARNING', '[WARNING]')
        output = output.replace('INFO', '[INFO]')
        return f'{output}'

    thread = Thread.Thread(target=run_command, args=(cmd,), daemon=True)
    thread.start()
    print(thread.is_alive())