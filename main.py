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
from server_utils.server_manager import get_all_servers
app = ctk.CTk()
app.geometry("720x480")
app.title("Tow Truck Server")

if os.name == 'nta':

    app.iconbitmap("./assets/images/window_icon.ico") # Remove ./clean when finished
else:
    messagebox.showwarning("OS not supported", "Non windows OS are not officially supported, please proceed with caution\nSee NonWindows.md for more information")
def on_tab_visibility(tab_window,other_window=None):
    def inner(event):
        # Get the notebook widget
        notebook = event.widget.nametowidget(event.widget.winfo_parent())
        print(type(notebook))
        # Get the index of the currently selected tab
        index = notebook.index(notebook.select())

        # Call corresponding function based on the index of the tab
        if index == 0:
            HomeScreen(tab_window,get_all_servers(),other_window)
        elif index == 1:
            AddServerScreen(tab_window)
            print("Add Server tab opened")
            # Call your function for the Add Server tab here
        elif index == 2:
            ManageServerFunction(tab_window)
            print("Manage Server tab opened")
            # Call your function for the Manage Server tab here
        elif index == 3:
            ShowCredits(tab_window)
            print("Credits tab opened")
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
    style.configure("Red.TFrame", background='#2b2b2b')  # Custom style for red background
    global manage_server_tab, home_tab, add_server_tab, credits_tab
    
    # Create a style for the notebook with vertical tabs
    style = ttk.Style()
    style.configure("Vertical.TNotebook", tabposition="wn")

    # Create a notebook (tabbed interface) with the custom style
    global notebook
    notebook = ttk.Notebook(app, style="Vertical.TNotebook")
    notebook.pack(fill='both', expand=True)
    
    manage_server_tab = ttk.Frame(notebook, style="Red.TFrame")

    home_tab = ttk.Frame(notebook, style="Red.TFrame")
    notebook.add(home_tab, text='', image=HomeIcon)
    home_tab.bind("<Visibility>", on_tab_visibility(home_tab, manage_server_tab))

    add_server_tab = ttk.Frame(notebook, style="Red.TFrame")
    notebook.add(add_server_tab, text='', image=AddServer_icon)
    add_server_tab.bind("<Visibility>", on_tab_visibility(add_server_tab))
    
    notebook.add(manage_server_tab, text='', image=ServersIcon)
    manage_server_tab.bind("<Visibility>", on_tab_visibility(manage_server_tab))
    
    credits_tab = ttk.Frame(notebook, style="Red.TFrame")
    notebook.add(credits_tab, text='Credits')
    credits_tab.bind("<Visibility>", on_tab_visibility(credits_tab))

sv_ttk.set_theme("dark")


main_screen()
app.mainloop()