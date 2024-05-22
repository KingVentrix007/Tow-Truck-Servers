import tkinter as tk
import customtkinter as ctk
import webbrowser


global credits_frame_ext
credits_frame_ext = None
made_credits = False
def ShowCredits(tab_view):
    global credits_frame_ext,made_credits
    if(credits_frame_ext is None):
        credits_frame = ctk.CTkFrame(tab_view)
        credits_frame_ext = credits_frame
    else:
        credits_frame = credits_frame_ext
    if(made_credits == False):
        credits_frame.pack(expand=True)
        ctk_label = ctk.CTkLabel(credits_frame, text="Thank you for using Tow Truck Servers", font=("Helvetica", 20), fg_color="#2b2b2b", cursor="hand2")
        ctk_label.pack()
        # Define the credits
        credits_list = [
            ("Tow Truck", "https://icons8.com/icon/CH8gN2XL5UPi/tow-truck"),
            ("Plus", "https://icons8.com/icon/21097/plus"),
            ("Bookmark", "https://icons8.com/icon/102297/bookmark"),
            ("No Image", "https://icons8.com/icon/1G2BW7-tQJJJ/no-image")
        ]

    # Display the credits as labels with clickable links
    
        ctk_label = ctk.CTkLabel(credits_frame, text="Credits", font=("Helvetica", 20, "bold"))
        ctk_label.pack(pady=10)

        ctk_label = ctk.CTkLabel(credits_frame, text="Thank you to Icons8 for", font=("Helvetica", 12))
        ctk_label.pack()

        for credit, link in credits_list:
            ctk_label = ctk.CTkLabel(credits_frame, text=credit, font=("Helvetica", 12), fg_color="#2b2b2b", cursor="hand2")
            ctk_label.pack(pady=5)
            ctk_label.bind("<Button-1>", lambda event, l=link: open_link(l))


        ctk_label = ctk.CTkLabel(credits_frame, text="Icons8.com", font=("Helvetica", 12), fg_color="#2b2b2b", cursor="hand2")
        ctk_label.pack()
        
        ctk_label.bind("<Button-1>", lambda event, l="https://icons8.com": open_link(l))
        made_credits = True

    def open_link(url):
        webbrowser.open_new(url)

class CreditsScreen(ctk.CTk):
    pass

def DisplayCredits():
    app = CreditsScreen()
    app.mainloop()

if __name__ == "__main__":
    DisplayCredits()
