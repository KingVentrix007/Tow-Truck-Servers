import tkinter 
import customtkinter


#  System Settings
customtkinter.set_appearance_mode("System")
customtkinter.set_appearance_mode("blue")

# App
app = customtkinter.CTk()
app.geometry("720x480")
app.title(" Tow Truck server")

#UI
AddServer = customtkinter.CTkButton(app,text="Add Server")
AddServer.place(relx=0.5, rely=0.5, anchor=customtkinter.CENTER)
ManageServer = customtkinter.CTkButton(app,text="Manage Server")
ManageServer.place(relx=0.5, rely=0.56, anchor=customtkinter.CENTER)
app.mainloop()