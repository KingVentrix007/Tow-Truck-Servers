import tkinter as tk
import customtkinter as ctk
import webbrowser

class CreditsScreen(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Credits")
        self.geometry("400x300")
        self.config(bg="#2b2b2b")
        # Center the window on the screen
        self.position_window()

        # Create a frame to hold the credits
        credits_frame = ctk.CTkFrame(self)
        
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
            ctk_label.bind("<Button-1>", lambda event, l=link: self.open_link(l))

        # ctk_label = ctk.CTkLabel(credits_frame, text=" for:", font=("Helvetica", 12))
        # ctk_label.pack()

        ctk_label = ctk.CTkLabel(credits_frame, text="Icons8.com", font=("Helvetica", 12), fg_color="#2b2b2b", cursor="hand2")
        ctk_label.pack()
        
        ctk_label.bind("<Button-1>", lambda event, l="https://icons8.com": self.open_link(l))

    def position_window(self):
        # Get the screen width and height
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Calculate x and y coordinates for the Tk root window
        x = int((screen_width / 2) - (400 / 2))
        y = int((screen_height / 2) - (300 / 2))

        self.geometry(f"400x300+{x}+{y}")

    def open_link(self, url):
        webbrowser.open_new(url)


def DisplayCredits():
    app = CreditsScreen()
    app.mainloop()

if __name__ == "__main__":
    DisplayCredits()
