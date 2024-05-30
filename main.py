# Main.py

import tkinter as tk
import customtkinter as ctk
from tkinter import ttk,messagebox
from PIL import Image, ImageTk
import sv_ttk
from ui.AddServerScreen import AddServerScreen
from ui.ManageServerFunction import ManageServerFunction
from ui.Credits import ShowCredits
from ui.HomeScreen import HomeScreen
import os
from config.globals import tab_icon_width,tab_icon_hight
from config.ui_config import default_color
from server_utils.server_manager import get_all_servers
import logging
app = ctk.CTk()
app.geometry("720x480")
app.title("Tow Truck Server")
default_theme = "Default.TFrame"
manage_server_tab = None

def setup_logging(log_file):
    """Setup logging configuration."""
    logging.basicConfig(filename=log_file, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
def log(*args):
    """Log a message."""
    message = ' '.join(map(str, args))
    logging.info(message)
if os.name == 'nt':

    app.iconbitmap("./assets/images/window_icon.ico") # Remove ./clean when finished
else:
    messagebox.showwarning("OS not supported", "Non windows OS are not officially supported, please proceed with caution\nSee NonWindows.md for more information")

def switch_to_ManageServerFunction():
    log("Switch to Manage Server Function")
    if(manage_server_tab is not None):
        log("Manage Server Function")
        ManageServerFunction(manage_server_tab)
    else:
        log("No Manage Server Function")
def on_tab_visibility(tab_window,other_window=None):
    def inner(event):
        # Get the notebook widget
        notebook = event.widget.nametowidget(event.widget.winfo_parent())
        log(type(notebook))
        # Get the index of the currently selected tab
        index = notebook.index(notebook.select())

        # Call corresponding function based on the index of the tab
        if index == 0:
            HomeScreen(tab_window,get_all_servers(),switch_to_ManageServerFunction)
        elif index == 1:
            AddServerScreen(tab_window)
            log("Add Server tab opened")
            # Call your function for the Add Server tab here
        elif index == 2:
            switch_to_ManageServerFunction()
            log("Manage Server tab opened")
            # Call your function for the Manage Server tab here
        elif index == 3:
            ShowCredits(tab_window)
            log("Credits tab opened")
            # Call your function for the Credits tab here
    return inner

AddServer_icon = Image.open("./assets/images/addserver_icon_80.png").resize((tab_icon_width, tab_icon_hight))
AddServer_icon = ImageTk.PhotoImage(AddServer_icon)
ServersIcon = Image.open("./assets/images/bookmark_100.png").resize((tab_icon_width, tab_icon_hight))
ServersIcon = ImageTk.PhotoImage(ServersIcon)
HomeIcon = Image.open("./assets/images/home-100.png").resize((tab_icon_width, tab_icon_hight))
HomeIcon = ImageTk.PhotoImage(HomeIcon)

def main_screen():
    style = ttk.Style()
    style.configure("Vertical.TNotebook", tabposition="wn")
    style.configure(default_theme, background='#2b2b2b')  # Custom style for red background
    global manage_server_tab, home_tab, add_server_tab, credits_tab
    
    # Create a style for the notebook with vertical tabs
    style = ttk.Style()
    style.configure("Vertical.TNotebook", tabposition="wn")

    # Create a notebook (tabbed interface) with the custom style
    global notebook
    notebook = ttk.Notebook(app, style="Vertical.TNotebook")
    notebook.pack(fill='both', expand=True)
    
    manage_server_tab = ttk.Frame(notebook, style=default_theme)

    home_tab = ttk.Frame(notebook, style=default_theme)
    notebook.add(home_tab, text='', image=HomeIcon)
    home_tab.bind("<Visibility>", on_tab_visibility(home_tab, manage_server_tab))

    add_server_tab = ttk.Frame(notebook, style=default_theme)
    notebook.add(add_server_tab, text='', image=AddServer_icon)
    add_server_tab.bind("<Visibility>", on_tab_visibility(add_server_tab))
    
    notebook.add(manage_server_tab, text='', image=ServersIcon)
    manage_server_tab.bind("<Visibility>", switch_to_ManageServerFunction())
    
    credits_tab = ttk.Frame(notebook, style=default_theme)
    notebook.add(credits_tab, text='Credits')
    credits_tab.bind("<Visibility>", on_tab_visibility(credits_tab))

sv_ttk.set_theme("dark")


main_screen()
app.after(100, switch_to_ManageServerFunction) # The delay of 100 milliseconds

app.mainloop()