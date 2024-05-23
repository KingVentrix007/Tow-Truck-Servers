# Main.py

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import sv_ttk
import customtkinter as ctk
from ui.AddServerScreen import AddServerScreen
from ui.ManageServerFunction import ManageServerFunction
from ui.Credits import ShowCredits
from ui.HomeScreen import HomeScreen
import pywinstyles
from config.globals import tab_icon_width,tab_icon_hight
from server_utils.server_manager import get_all_servers
app = tk.Tk()
app.geometry("720x480")
app.title("Tow Truck Server")
app.iconbitmap("./assets/images/window_icon.ico") # Remove ./clean when finished
pywinstyles.apply_style(app, 'mica')
def on_tab_visibility(tab_window):
    def inner(event):
        # Get the notebook widget
        notebook = event.widget.nametowidget(event.widget.winfo_parent())
        print(type(notebook))
        # Get the index of the currently selected tab
        index = notebook.index(notebook.select())

        # Call corresponding function based on the index of the tab
        if index == 0:
            HomeScreen(tab_window,get_all_servers())
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

AddServer_icon = Image.open("./img/addserver_icon_80.png").resize((tab_icon_width, tab_icon_hight))
AddServer_icon = ImageTk.PhotoImage(AddServer_icon)
ServersIcon = Image.open("./img/bookmark_100.png").resize((tab_icon_width, tab_icon_hight))
ServersIcon = ImageTk.PhotoImage(ServersIcon)

def main_screen():
    # Create a style for the notebook with vertical tabs
    style = ttk.Style()
    style.configure("Vertical.TNotebook", tabposition="wn")

    # Create a notebook (tabbed interface) with the custom style
    global notebook
    notebook = ttk.Notebook(app, style="Vertical.TNotebook")
    notebook.pack(fill='both', expand=True)
    global home_tab
    home_tab = ttk.Frame(notebook)
    notebook.add(home_tab, text='Home')
    home_tab.bind("<Visibility>", on_tab_visibility(home_tab))

    # Create the Add Server tab
    global add_server_tab
    add_server_tab = ttk.Frame(notebook)
    notebook.add(add_server_tab, text='',image=AddServer_icon)
    add_server_tab.bind("<Visibility>", on_tab_visibility(add_server_tab))
    manage_server_tab = ttk.Frame(notebook)
    notebook.add(manage_server_tab, text='',image=ServersIcon)
    manage_server_tab.bind("<Visibility>", on_tab_visibility(manage_server_tab))
    # Add the Credits tab
    global credits_tab
    credits_tab = ttk.Frame(notebook)
    notebook.add(credits_tab, text='Credits')
    credits_tab.bind("<Visibility>", on_tab_visibility(credits_tab))
sv_ttk.set_theme("dark")

main_screen()
app.mainloop()