import tkinter as tk

from tkinter import messagebox


import customtkinter as ctk
from ui.general import clear_window
from server_utils.server_manager import save_properties
from config.ui_config import default_color
def validate_int_input(P):
    if P.isdigit() or P == "":
        return True
    return False
def edit_properties_window(properties, file_path):
    settings_window = ctk.CTk()
    settings_window.title(properties.get("displayName",'Server'))

    # clear_window(window)
    def save_changes():
        for key, widget in widgets.items():
            if isinstance(widget, tk.BooleanVar):
                properties[key] = 'true' if widget.get() else 'false'
            else:
                properties[key] = widget.get()
        save_properties(file_path, properties)
        settings_window.destroy()
        messagebox.showinfo("Save", "Properties saved successfully")


    def on_mousewheel(event):
        canvas.yview_scroll(-1 * int(event.delta / 120), "units")

    main_frame = ctk.CTkFrame(settings_window)
    main_frame.pack(fill=tk.BOTH, expand=True)
    # main_frame.config(bg=default_color)
    canvas = ctk.CTkCanvas(main_frame,bg=default_color)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = ctk.CTkScrollbar(main_frame, orientation=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    canvas.configure(yscrollcommand=scrollbar.set,borderwidth=0,highlightthickness=0)
    canvas.bind_all("<MouseWheel>", on_mousewheel)

    sub_frame = ctk.CTkFrame(canvas)
    # sub_frame.configure(borderwidth=0)
    canvas.create_window((0, 0), window=sub_frame, anchor="nw")

    widgets = {}
    row = 0

    vcmd = (settings_window.register(validate_int_input), '%P')

    for key, value in properties.items():
        label = ctk.CTkLabel(sub_frame, text=key)
        label.grid(row=row, column=0, sticky='w', padx=5, pady=5)

        if value.lower() in ('true', 'false'):
            var = tk.BooleanVar(value=value.lower() == 'true')
            checkbox = ctk.CTkCheckBox(sub_frame, variable=var,text="")
            checkbox.grid(row=row, column=1, sticky='w', padx=5, pady=5)
            widgets[key] = var
        elif value.isdigit():
            entry = ctk.CTkEntry(sub_frame, validate='key', validatecommand=vcmd)
            entry.insert(0, value)
            entry.grid(row=row, column=1, sticky='w', padx=5, pady=5)
            widgets[key] = entry
        else:
            entry = ctk.CTkEntry(sub_frame)
            entry.insert(0, value)
            entry.grid(row=row, column=1, sticky='w', padx=5, pady=5)
            widgets[key] = entry

        row += 1

    sub_frame.update_idletasks()  # Ensure sub_frame is updated with widgets
    canvas.config(scrollregion=canvas.bbox("all"))  # Update scroll region
    save_button = ctk.CTkButton(settings_window, text="Save", command=save_changes)
    save_button.pack(side=tk.RIGHT, padx=5, pady=5, fill=tk.X)
    settings_window.mainloop()
