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


def run_command(command, output_widget):
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
    command = ["java", "-jar", jar_file, "--installServer"]
    thread = Thread(target=run_command, args=(command, output_widget))
    thread.start()
    root.mainloop()

