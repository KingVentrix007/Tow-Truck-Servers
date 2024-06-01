from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but they might need fine-tuning.
build_exe_options = {
}

setup(
    name="Tow Truck Servers",
    version="0.1",
    description="Minecraft Server Wrapper",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base="gui")],
)