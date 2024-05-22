import tkinter as tk
from tkinter import ttk
import sv_ttk
def show_frame(frame):
    frame.tkraise()

root = tk.Tk()
root.title("Vertical Tabs Example")
root.geometry("600x400")

main_frame = ttk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=1)

tab_frame = ttk.Frame(main_frame, width=100)
tab_frame.pack(side=tk.LEFT, fill=tk.Y)

content_frame = ttk.Frame(main_frame)
content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=1)

tab1_frame = ttk.Frame(content_frame)
tab1_frame.grid(row=0, column=0, sticky='nsew')

tab2_frame = ttk.Frame(content_frame)
tab2_frame.grid(row=0, column=0, sticky='nsew')

tab3_frame = ttk.Frame(content_frame)
tab3_frame.grid(row=0, column=0, sticky='nsew')

ttk.Label(tab1_frame, text="This is Tab 1").pack(padx=10, pady=10)
ttk.Label(tab2_frame, text="This is Tab 2").pack(padx=10, pady=10)
ttk.Label(tab3_frame, text="This is Tab 3").pack(padx=10, pady=10)

tab1_button = ttk.Button(tab_frame, text="Tab 1", command=lambda: show_frame(tab1_frame))
tab1_button.pack(fill=tk.X)

tab2_button = ttk.Button(tab_frame, text="Tab 2", command=lambda: show_frame(tab2_frame))
tab2_button.pack(fill=tk.X)

tab3_button = ttk.Button(tab_frame, text="Tab 3", command=lambda: show_frame(tab3_frame))
tab3_button.pack(fill=tk.X)

show_frame(tab1_frame)
sv_ttk.set_theme("dark")
root.mainloop()
