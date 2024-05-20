def ManageServerFunction():
    clear_window()

    servers = get_all_servers()

    def create_server_window(server_info):
        global process  # Ensure process is global

        def open_settings():
            path = server_info.get('path', "/fake/")
            properties_file = os.path.join(path, "server.properties")
            print("properties_file ==",properties_file)
            if os.path.exists(properties_file):
                properties = load_properties(properties_file)
                edit_properties_window(properties, properties_file)
            else:
                messagebox.showerror("Error", f"server.properties file not found at {properties_file}")

        def run_server():
            global process  # Ensure process is global
            adjust_path()

            path = server_info.get('path', "/fake/")
            java = server_info.get('javaPath', "java")
            os.chdir(path)
            print("PATH == ", os.getcwd())
            lib = makeserver.extract_libraries_path("run.bat")
            ram = server_info.get('ram', "2G")
            cmd = f"{java} -Xmx{ram} {lib} nogui %*"

            def run_command(command):
                global process  # Ensure process is global
                print(command)
                process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
                for line in iter(process.stdout.readline, ""):
                    print(line)
                    formatted_output = format_output_as_html(line)
                    try:
                        text_widget.insert(tk.END, formatted_output)
                        text_widget.see(tk.END)  # Auto-scroll to the end
                    except Exception as e:
                        pass
                process.stdout.close()
                process.wait()

            def format_output_as_html(output):
                output = output.replace('ERROR', '[ERROR]')
                output = output.replace('WARNING', '[WARNING]')
                output = output.replace('INFO', '[INFO]')
                return f'{output}'

            thread = threading.Thread(target=run_command, args=(cmd,), daemon=True)
            thread.start()
            print(thread.is_alive())

        def send_command():
            global process  # Ensure process is global
            command = command_entry.get()
            print("command")
            print("Process == ", process)
            print("process.stdin == ", process.stdin)
            if process and process.stdin:
                print("command is being run\n")
                process.stdin.write(command + "\n")
                process.stdin.flush()

        def del_server_callback():
            # server_window.destroy()
            del_server(server_info.get('displayName', "Unnamed Server"))
        def back():
            clear_window()
            ManageServerFunction()
        # clear_window()
        server_window = ctk.CTk()
        server_window.geometry("800x600")
        server_window.title(server_info.get('displayName', "Server"))

        # Create a frame for the top menu bar
        menu_bar = ctk.CTkFrame(server_window)
        menu_bar.pack(side=tk.TOP, fill=tk.X)

        delete_button = ctk.CTkButton(menu_bar, text="Delete", command=del_server_callback)
        delete_button.pack(side=tk.LEFT, padx=5, pady=5)
        back_button = ctk.CTkButton(menu_bar,text="Back", command=back)
        run_button = ctk.CTkButton(menu_bar, text="Run", command=run_server)
        run_button.pack(side=tk.LEFT, padx=5, pady=5)

        settings_button = ctk.CTkButton(menu_bar, text="Settings", command=open_settings)
        settings_button.pack(side=tk.LEFT, padx=5, pady=5)

        mod_btn = ctk.CTkButton(menu_bar, text="Mod Menu",command=lambda: mod_menu(server_info.get('path','null')))
        mod_btn.pack(side=tk.LEFT, padx=5, pady=5)
        # back_button.pack(side=tk.LEFT,padx=5, pady=5)
        text_widget = ScrolledText(server_window, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True)

        command_entry = ctk.CTkEntry(server_window)
        command_entry.pack(fill=tk.X, pady=5)

        send_button = ctk.CTkButton(server_window, text="Send Command", command=send_command)
        send_button.pack(pady=5)

        server_window.mainloop()
    for idx, server in enumerate(servers):
        display_name = server.get('displayName', f"Server {idx+1}")
        server_button = customtkinter.CTkButton(app, text=display_name, command=lambda server_info=server: create_server_window(server_info))
        server_button.grid(row=idx, column=0, padx=10, pady=5)

    back_button = customtkinter.CTkButton(app, text="Back", command=main_screen)
    back_button.grid(row=len(servers), column=0, pady=10)