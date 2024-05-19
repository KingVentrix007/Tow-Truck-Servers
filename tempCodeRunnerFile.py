def mod_menu(path):
    window = ctk.CTk()
    window.title("Mod Menu")
    window.geometry("800x600")

    canvas = ctk.CTkCanvas(window)
    canvas.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)

    scrollbar = ctk.CTkScrollbar(window, command=canvas.yview)
    scrollbar.pack(side=ctk.RIGHT, fill=ctk.Y)

    canvas.configure(yscrollcommand=scrollbar.set)

    frame = ctk.CTkFrame(canvas)
    canvas.create_window((0, 0), window=frame, anchor=ctk.NW)

    mod_path = os.path.join(path, "mods")

    # Function to toggle mod activation
    def toggle_mod(mod_button):
        mod_button.configure(state=ctk.DISABLED if mod_button.cget('state') == 'normal' else ctk.NORMAL)
        # Modify the file extension to .disabled or .jar
        mod_file = mod_button.configure('text')[-1]
        mod_file_path = os.path.join(mod_path, mod_file)
        new_file_extension = '.disabled' if mod_button.conconfigurefig('state')[-1] == 'disabled' else '.jar'
        os.rename(mod_file_path, mod_file_path.replace('.jar', new_file_extension))

    # List all files in the mods directory
    mod_files = [file for file in os.listdir(mod_path) if file.endswith('.jar')]

    # Create a button for each mod
    for mod_file in mod_files:
        mod_button = ctk.CTkButton(frame, text=mod_file, command=lambda f=mod_file: toggle_mod(mod_button))
        mod_button.pack(side=ctk.TOP, anchor=ctk.W)

    def on_configure(event):
        canvas.configure(scrollregion=canvas.bbox('all'))

    frame.bind('<Configure>', on_configure)

    # Position the frame on the left side of the window
    frame.pack(side=ctk.LEFT, fill=ctk.Y)

    window.mainloop()