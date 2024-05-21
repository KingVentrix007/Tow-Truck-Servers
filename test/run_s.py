def run_server():
            messagebox.showerror("Server", f"Currently Unsupported")
            return
            global process  # Ensure process is global
            adjust_path()

            path = server_info.get('path', "/fake/")
            java = server_info.get('javaPath', "java")
            os.chdir(path)
            print("PATH == ", os.getcwd())
            lib = extract_libraries_path("run.bat")
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