import tkinter as tk
import customtkinter
from PIL import Image, ImageTk
from ui.general import clear_window
from config.ui_config import main_icons_width,main_icons_hight
from ui.AddServerScreen import AddServerScreen
from ui.ManageServerFunction import ManageServerFunction
customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")
app = customtkinter.CTk()
app.geometry("720x480")
app.title("Tow Truck Server")
app.iconbitmap("./clean/assets/images/window_icon.ico") #Remove ./clean when finished

def main_screen():
    clear_window(app)

    # Create a frame for the side menu
    side_menu = customtkinter.CTkFrame(app, width=200)
    side_menu.place(relx=0.0, rely=0.0, relheight=1.0, anchor='nw')
    
    # Define the dimensions for the icons and buttons
    # main_icons_width = 80
    # main_icons_height = 80

    AddServer_icon = customtkinter.CTkImage(
        light_image=Image.open('./img/addserver_icon_80.png'),
        dark_image=Image.open('./img/addserver_icon_80.png'),
        size=(main_icons_width, main_icons_hight)
    )
    AddServer = customtkinter.CTkButton(
        side_menu,
        text="",
        command=lambda:AddServerScreen(app,main_screen),
        image=AddServer_icon,
        width=main_icons_width,
        height=main_icons_hight
    )
    AddServer.pack(pady=10, padx=10)
    # Tooltip(AddServer, "Add a new server")

    ManageServer_icon = customtkinter.CTkImage(
        light_image=Image.open('./img/bookmark_100.png'),
        dark_image=Image.open('./img/bookmark_100.png'),
        size=(main_icons_width, main_icons_hight)
    )
    ManageServer = customtkinter.CTkButton(
        side_menu,
        text="",
        command=lambda: ManageServerFunction(app,main_screen),
        image=ManageServer_icon,
        width=main_icons_width,
        height=main_icons_hight
    )
    ManageServer.pack(pady=10, padx=10)
    # Tooltip(ManageServer, "Manage existing servers")

    # # Add the Credits button at the bottom of the side menu
    # Credits = customtkinter.CTkButton(
    #     side_menu,
    #     text="Credits",
    #     width=main_icons_width,
    #     height=main_icons_hight
    # )
    # Credits.pack(pady=10, padx=10, side='bottom')
    # Tooltip(Credits, "View credits")

main_screen()
app.mainloop()
