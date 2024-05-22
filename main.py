import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import sv_ttk
from ui.AddServerScreen import AddServerScreen
from ui.ManageServerFunction import ManageServerFunction
from ui.Credits import ShowCredits
app = tk.Tk()
app.geometry("720x480")
app.title("Tow Truck Server")
app.iconbitmap("./assets/images/window_icon.ico") # Remove ./clean when finished

def on_tab_visibility(tab_window):
    def inner(event):
        # Get the notebook widget
        notebook = event.widget.nametowidget(event.widget.winfo_parent())

        # Get the index of the currently selected tab
        index = notebook.index(notebook.select())

        # Call corresponding function based on the index of the tab
        if index == 0:
            AddServerScreen(tab_window)
            print("Add Server tab opened")
            # Call your function for the Add Server tab here
        elif index == 1:
            ManageServerFunction(tab_window)
            print("Manage Server tab opened")
            # Call your function for the Manage Server tab here
        elif index == 2:
            ShowCredits(tab_window)
            print("Credits tab opened")
            # Call your function for the Credits tab here
    return inner


def main_screen():
    # Create a style for the notebook with vertical tabs
    style = ttk.Style()
    style.configure("Vertical.TNotebook", tabposition="wn")

    # Create a notebook (tabbed interface) with the custom style
    global notebook
    notebook = ttk.Notebook(app, style="Vertical.TNotebook")
    notebook.pack(fill='both', expand=True)

    # Create the Add Server tab
    global add_server_tab
    add_server_tab = ttk.Frame(notebook)
    notebook.add(add_server_tab, text='Add Server')
    add_server_tab.bind("<Visibility>", on_tab_visibility(add_server_tab))

    AddServer_icon = Image.open('./img/addserver_icon_80.png').resize((80, 80), Image.BICUBIC)
    AddServer_icon = ImageTk.PhotoImage(AddServer_icon)
    AddServer_label = tk.Label(add_server_tab, image=AddServer_icon)
    AddServer_label.pack(pady=10, padx=10)

    # Create the Manage Server tab
    global manage_server_tab
    manage_server_tab = ttk.Frame(notebook)
    notebook.add(manage_server_tab, text='Manage Server')
    manage_server_tab.bind("<Visibility>", on_tab_visibility(manage_server_tab))
    # Add the Credits tab
    global credits_tab
    credits_tab = ttk.Frame(notebook)
    notebook.add(credits_tab, text='Credits')
    credits_tab.bind("<Visibility>", on_tab_visibility(credits_tab))
sv_ttk.set_theme("dark")

main_screen()
app.mainloop()